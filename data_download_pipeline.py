from concurrent.futures import ThreadPoolExecutor, as_completed
import dask.dataframe as dd
import pandas as pd
import os
import time
import threading
from collections import deque
import pyotp
import json
from datetime import date
import requests
import zipfile36 as zipfile
from NorenRestApiPy.NorenApi import  NorenApi
#from threading import Timer
import time
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def token_download(path: str) -> None:
    """
    Download NSE and BSE token master files (Spot, Futures, Options).
    Extracts token files from the Shoonya API and saves them to the given path.  

    Args:
        path (str): Directory where extracted token files will be saved.

    Notes:
        - Downloads zipped token files (`NFO`, `NSE`, `BFO`, `BSE`).
        - Extracts and removes the zip files after extraction.
    """
    root = 'https://api.shoonya.com/'
    masters = ['NFO_symbols.txt.zip', 'NSE_symbols.txt.zip', 'BFO_symbols.txt.zip', 'BSE_symbols.txt.zip']

    for zip_file in masters:
        logging.info(f"Downloading {zip_file}")
        url = root + zip_file
        r = requests.get(url, allow_redirects=True)

        # Save the downloaded zip file
        with open(zip_file, 'wb') as f:
            f.write(r.content)

        try:
            with zipfile.ZipFile(zip_file) as z:
                z.extractall(path)
                logging.info(f"Extracted: {zip_file}")
        except Exception:
            logging.error("❌ Invalid file")

        # Clean up the zip file
        os.remove(zip_file)
        logging.info(f"Removed: {zip_file}")


def get_time(time_string: str) -> float:
    """
    Convert datetime string into Shoonya-compatible epoch timestamp.

    Args:
        time_string (str): DateTime string in format '%d-%m-%Y %H:%M:%S'

    Returns:
        float: Epoch timestamp (Shoonya API compatible)

    Example:
        >>> get_time("26-07-2024 15:30:00")
        1721988000.0
    """
    data = time.strptime(time_string, '%d-%m-%Y %H:%M:%S')
    return time.mktime(data)


def get_login_credintial():
    """
    Read login credentials from config.json.

    Returns:
        tuple: (token, user, password, vc, app_key)
    """
    with open("config.json", "r") as f:
        config = json.load(f)

    return config["token"], config["user"], config["pwd"], config["vc"], config["app_key"]


def ShoonyaApiLogin(token: str, user: str, pwd: str, vc: str, app_key: str):
    """
    Login to Shoonya API using credentials.

    Args:
        token (str): TOTP token key for 2FA.
        user (str): User ID.
        pwd (str): Password.
        vc (str): Vendor code.
        app_key (str): API secret key.

    Returns:
        NorenApi: Authenticated API session object.
    """
    class ShoonyaApiPy(NorenApi):
        def __init__(self):
            super().__init__(host='https://api.shoonya.com/NorenWClientTP/',
                             websocket='wss://api.shoonya.com/NorenWSTP/')

    api = ShoonyaApiPy()
    factor2 = pyotp.TOTP(token).now()  # Generate dynamic OTP
    imei = 'abc1234'

    # Perform login
    ret = api.login(userid=user, password=pwd, twoFA=factor2,
                    vendor_code=vc, api_secret=app_key, imei=imei)
    return api


def safe_get_time_price_series(api, exch: str, token: str, start_time: float, end_time: float):
    """
    Fetch historical 1-min time series data safely from Shoonya API.

    Args:
        api (NorenApi): Logged-in API object.
        exch (str): Exchange name ("NSE"/"BSE"/"NFO").
        token (str): Instrument token.
        start_time (float): Start epoch timestamp.
        end_time (float): End epoch timestamp.

    Returns:
        list[dict] | None: List of candles or None if error occurs.
    """
    try:
        ret = api.get_time_price_series(
            exchange=exch,
            token=str(token),
            starttime=start_time,
            endtime=end_time,
            interval=1
        )

        if ret is None:
            logging.error(f"❌ No data returned for Token: {token}")
        elif isinstance(ret, dict) and ret.get("stat") != "Ok":
            logging.error(f"❌ API Error: {ret}")
        else:
            logging.info("✅ Data received")
            return ret

    except Exception as e:
        logging.error(f"❌ Exception occurred: {e}")
        return None


def token_formating(token_path: str) -> pd.DataFrame:
    """
    Format and filter token files for Spot, Futures, and Options (NSE/BSE).

    Args:
        token_path (str): Path where token files are stored.

    Returns:
        pd.DataFrame: Consolidated DataFrame of valid tokens.
    """
    # Read NSE spot and F&O token files
    all_token_spot = pd.read_csv(token_path + '\\NSE_symbols.txt')
    all_token_NFO = pd.read_csv(token_path + '\\NFO_symbols.txt')
    bse_token_NFO = pd.read_csv(token_path + '\\BFO_symbols.txt')

    # Drop unnecessary columns
    spot_columns_to_drop = ['LotSize', 'TickSize', 'Unnamed: 7']
    fno_columns_to_drop = ['LotSize', 'TickSize', 'Unnamed: 10']
    all_token_spot.drop(columns=spot_columns_to_drop, inplace=True)
    all_token_NFO.drop(columns=fno_columns_to_drop, inplace=True)

    # Filter F&O stock list
    fno_stocks_list = list(all_token_NFO[all_token_NFO['Instrument'] == 'OPTSTK'].Symbol.unique())

    # Underlying tokens
    underlying_stock_token = all_token_spot[(all_token_spot['Instrument'] == "EQ") &
                                            (all_token_spot['Symbol'].isin(fno_stocks_list))]
    underlying_index_token = all_token_spot[all_token_spot['Instrument'] == 'INDEX']

    # Derivative tokens
    derivative_index_token = all_token_NFO[all_token_NFO['Instrument'].isin(['FUTIDX', 'OPTIDX'])]
    derivative_stock_token = all_token_NFO[(all_token_NFO['Instrument'].isin(['FUTSTK', 'OPTSTK'])) &
                                           (all_token_NFO['Symbol'].isin(fno_stocks_list))]

    # BSE F&O tokens (Sensex only)
    bse_token_NFO.drop(columns=fno_columns_to_drop, inplace=True)
    sensex_fut_option_tokens = bse_token_NFO[bse_token_NFO['Symbol'].isin(['BSXOPT', 'BSXFUT'])]

    # Merge all
    dfs = [underlying_stock_token, underlying_index_token,
           derivative_index_token, derivative_stock_token,
           sensex_fut_option_tokens]

    nse_index_stock_token = pd.concat(dfs, axis=0).reset_index(drop=True)

    # Standardize index symbols
    mapping = {
        "Nifty 50": "NIFTY",
        "Nifty Bank": "BANKNIFTY",
        "Nifty Next 50": "NIFTYNXT50",
        "Nifty Fin Services": "FINNIFTY",
        "NIFTY MID SELECT": "MIDCPNIFTY",
        "INDIAVIX": "INDIAVIX"
    }
    nse_index_stock_token.loc[nse_index_stock_token['Instrument'] == 'INDEX', 'Symbol'] = (
        nse_index_stock_token.loc[nse_index_stock_token['Instrument'] == 'INDEX', 'Symbol'].map(mapping)
    )

    return nse_index_stock_token


def add_token_info(df: pd.DataFrame, stock_df: pd.DataFrame, token: str) -> pd.DataFrame:
    """
    Enrich Shoonya API OHLCV data with token-related metadata in a vectorized way.

    Args:
        df (pd.DataFrame): Raw Shoonya data (time series).
        stock_df (pd.DataFrame): Token reference DataFrame containing metadata.
        token (str): Instrument token (string or int).

    Returns:
        pd.DataFrame: Enriched DataFrame with symbol, expiry, option type, etc.
    """
    #Rename columns for consistency
    df = df.rename(
        columns={'time': 'datetime', 'into': 'open', 'inth': 'high',
                 'intl': 'low', 'intc': 'close'}
    ).copy()

    #Split datetime into date and time
    df['date'] = df['datetime'].str.split(" ").str[0]
    df['time'] = df['datetime'].str.split(" ").str[1]

    #Keep only relevant stock_df row for this token
    meta = stock_df.loc[stock_df['Token'] == token, 
                        ['Token', 'Symbol', 'TradingSymbol', 'Expiry', 
                         'OptionType', 'StrikePrice', 'Instrument']].copy()

    if meta.empty:
        raise ValueError(f"❌ Token {token} not found in stock_df.")

    #Ensure 'Token' column exists in df for merge
    df['Token'] = token

    #Merge df with token metadata (vectorized)
    df = df.merge(meta, on="Token", how="left")

    #Reorder columns for readability
    df = df[['Symbol', 'date', 'time', 'TradingSymbol', 'Instrument',
             'Expiry', 'OptionType', 'StrikePrice', 'open', 'high',
             'low', 'close', 'intvwap', 'intv', 'intoi', 'v', 'oi',
             'ssboe', 'stat']]

    #Rename back to match expected output
    df.rename(columns={
        'Symbol': 'symbol',
        'TradingSymbol': 'trading_symbol',
        'Expiry': 'exp_date',
        'OptionType': 'option_type',
        'StrikePrice': 'strike_price',
        'Instrument': 'instrument'
    }, inplace=True)

    return df


def save_csv(save_path: str, df: pd.DataFrame, filename: str, index: bool = False) -> None:
    """
    Save DataFrame to CSV file.

    Args:
        save_path (str): Directory to save CSV.
        df (pd.DataFrame): DataFrame to save.
        filename (str): CSV filename.
        index (bool): Whether to write row indices. Default = False.
    """
    os.makedirs(save_path, exist_ok=True)

    if not filename.lower().endswith(".csv"):
        filename += ".csv"

    file_path = os.path.join(save_path, filename)
    df.to_csv(file_path, index=index)
    logging.info(f"File saved at: {file_path}")




# ---------------------- API Rate Limiter ----------------------
class RateLimiter:
    """
    Rate limiter: max_calls per interval (seconds).
    Example: RateLimiter(10, 1) → 10 calls per second for Finwesiya
             RateLimiter(200, 60) → 200 calls per minute for finwesiya
    """
    def __init__(self, max_calls, interval):
        self.max_calls = max_calls
        self.interval = interval
        self.lock = threading.Lock()
        self.calls = deque()

    def acquire(self):
        with self.lock:
            now = time.time()

            # remove calls older than interval
            while self.calls and now - self.calls[0] > self.interval:
                self.calls.popleft()

            if len(self.calls) >= self.max_calls:
                sleep_time = self.interval - (now - self.calls[0])
                time.sleep(max(sleep_time, 0))

            self.calls.append(time.time())



# Global limiters for Shoonya API
per_second_limiter = RateLimiter(20, 1)      # 20 calls/sec
# per_minute_limiter = RateLimiter(200, 60)    # 200 calls/min


def fetch_token_data(api, token, exch, start_time, end_time, stock_df, symbol):
    """
    Download intraday data for a single token with rate limiting.
    """

    # Enforce rate limits
    per_second_limiter.acquire()
    # per_minute_limiter.acquire()

    ret = safe_get_time_price_series(api, exch, token, start_time, end_time)
    if ret:
        try:
            df = pd.DataFrame.from_dict(ret)
            df = add_token_info(df, stock_df, token)
            return df
        except Exception as e:
            print(f"❌ Error processing token {token} for {symbol}: {e}")
            return None
    return None

def data_download(save_path: str, 
                  token_save_path: str, 
                  start_timestamp: str, 
                  end_timestamp: str,
                  max_workers: int = 10
                  ) -> None:


    """
    Optimized Data Download Pipeline with rate limiting:
    - Parallel token fetching using ThreadPoolExecutor
    - Enforces Shoonya API limits (10/sec, 200/min)
    - Saves results in Parquet format
    """

    # Suppress DEBUG logs
    logging.getLogger("NorenRestApiPy").setLevel(logging.ERROR)
    logging.getLogger("urllib3").setLevel(logging.ERROR)


    start_time = get_time(start_timestamp)
    end_time   = get_time(end_timestamp)


    # Token folder (daily)
    current_date = time.strftime('%Y-%m-%d', time.localtime())
    token_path = os.path.join(token_save_path, current_date)
    os.makedirs(token_path, exist_ok=True)

    # Download tokens if not already
    token_download(token_path)
    nse_tokens = token_formating(token_path)

    # Login API
    token, user, password, vc, app_key = get_login_credintial()
    api = ShoonyaApiLogin(token=token, user=user, pwd=password, vc=vc, app_key=app_key)

    ##########   DATA Downloading Block
    for symbol in nse_tokens.Symbol.unique()[:20]:   # limit for testing
        print(f"📥 Downloading data for {symbol}...")

        temp_stock_df = nse_tokens[nse_tokens['Symbol'] == symbol]
        futures = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for token in temp_stock_df['Token'].unique():
                exch = temp_stock_df[temp_stock_df['Token']==token]['Exchange'].iloc[0]
                futures.append(
                    executor.submit(fetch_token_data, api, token, exch,
                                    start_time, end_time, temp_stock_df, symbol)
                )

            results = [f.result() for f in as_completed(futures) if f.result() is not None]

        if not results:
            print(f"⚠️ No data found for {symbol}")
            continue

        # # Convert to Dask DataFrame
        # big_df = dd.from_pandas(pd.concat(results, axis=0), npartitions=8)

        # Combine all results for this symbol
        if results:
            final_df = pd.concat(results, ignore_index=True)


        # # Save as Parquet
        # symbol_path = os.path.join(save_path, current_date)
        # os.makedirs(symbol_path, exist_ok=True)
        # filename = f"{symbol}_{current_date}.parquet"
        # big_df.to_parquet(os.path.join(symbol_path, filename), engine="pyarrow", overwrite=True)
        # print(f"✅ Saved {symbol} data to {filename}")

            #Save one parquet file per symbol
            symbol_path = os.path.join(save_path, current_date)
            os.makedirs(symbol_path, exist_ok=True)
            output_file = os.path.join(symbol_path, f"{symbol}.parquet")
            final_df.to_parquet(output_file, index=False)   # single file, not multiple parts
            print(f"✅ Saved {symbol} data to {output_file}")