import pandas as pd
from datetime import date
import os
import requests
import zipfile36 as zipfile
from NorenRestApiPy.NorenApi import  NorenApi
#from threading import Timer
import time
import logging
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

import pyotp

# import warnings
# warnings.filterwarnings('ignore')

def token_download(path):

    '''
    This Function Will download all tokens for NSE and BSE. 
    Future and OPtions Tokens for NSE and BSE is also included
    And save the txt file in directory, which you will mention in path (input of function)
    '''

    root = 'https://api.shoonya.com/'
    #root = 'https://shoonya.com/api-documentation#symbolmaster'
    #For FnO token download
    masters = ['NFO_symbols.txt.zip', 'NSE_symbols.txt.zip', 'BFO_symbols.txt.zip', 'BSE_symbols.txt.zip'] #'CDS_symbols.txt.zip', 'MCX_symbols.txt.zip', 'BSE_symbols.txt.zip'

    for zip_file in masters:    
        # print(f'downloading {zip_file}')
        logging.info(f"Downloading {zip_file}")
        url = root + zip_file
        r = requests.get(url, allow_redirects=True)
        
        # Write the content to a zip file
        with open(zip_file, 'wb') as f:
            f.write(r.content)
    
        try:
            with zipfile.ZipFile(zip_file) as z:
                # path = "E:\\FnO_Stocks_Intraday_data_download\\token"
                # path = os.getcwd()
                #Extacting the file and saving into the path directory
                z.extractall(path)
                print("Extracted: ", zip_file)
        except:
            # print("Invalid file")
            logging.error("❌ Invalid file")


        os.remove(zip_file)
        print(f'remove: {zip_file}')
    


def get_time(time_string):

    '''
    This Function will convert the object date timestamp into a format which is required for shoonya api
    input format: "26-07-2024 15:30:00"
    output format: 1721988000.0
    '''

    data = time.strptime(time_string,'%d-%m-%Y %H:%M:%S')
    return time.mktime(data)


def ShoonyaApiLogin(token, user, pwd, vc, app_key):

    api = None
    class ShoonyaApiPy(NorenApi):
        def __init__(self):
            NorenApi.__init__(self, host='https://api.shoonya.com/NorenWClientTP/', websocket='wss://api.shoonya.com/NorenWSTP/')        


    #enable dbug to see request and responses
    logging.basicConfig(level=logging.DEBUG)

    #start of our program
    api = ShoonyaApiPy()

    #credentials
    ##################### Prism Password = Rajraj@88
    ##################### Shoonya Password = Rajraj@88  ########## both are same

    factor2 = pyotp.TOTP(token).now()
    imei    = 'abc1234'

    #make the api call
    ret = api.login(userid=user, password=pwd, twoFA=factor2, vendor_code=vc, api_secret=app_key, imei=imei)

    # print(ret)
    return api



# -----------------------------------------------------------
# Example: safe API call with custom error handling
# -----------------------------------------------------------
def safe_get_time_price_series(api, exch, token, start_time, end_time):
    try:
        ret = api.get_time_price_series(
            exchange=exch,
            token=str(token),
            starttime=start_time,
            endtime=end_time,
            interval=1
        )

        # Handle Shoonya-style error response
        if ret is None:
            print("❌ No data returned")
        elif isinstance(ret, dict) and ret.get("stat") != "Ok":
            print(f"❌ API Error: {ret}")
        else:
            print("✅ Data received")
            return ret

    except Exception as e:
        print(f"❌ Exception occurred: {e}")
        return None



def token_formating(token_path):

    ############# TOKEN Extraction Block
    '''
    Extracting Spot, option and future token for all Future and Option stocks and index
    all index included
    '''
    #reading spot token file
    ##'E:\\FnO_Stocks_Intraday_data_download\\token
    all_token_spot = pd.read_csv(token_path + '\\NSE_symbols.txt')

    all_token_NFO = pd.read_csv(token_path + '\\NFO_symbols.txt')

    bse_token_NFO = pd.read_csv(token_path + '\\BFO_symbols.txt')
    #BSXOPT SYMBOL FOR SENSEX INDEX
    #BSXFUT Symbol for future of sensex index

    spot_columns_to_drop = ['LotSize', 'TickSize', 'Unnamed: 7']
    fno_columns_to_drop = ['LotSize', 'TickSize', 'Unnamed: 10']
    all_token_spot.drop(columns=spot_columns_to_drop, inplace=True)
    all_token_NFO.drop(columns=fno_columns_to_drop, inplace=True)
    
    # Future and Options Stocks list
    fno_stocks_list = list(all_token_NFO[all_token_NFO['Instrument']=='OPTSTK'].Symbol.unique())

    #This spot token include all Stocks having their derivatives
    underlying_stock_token = all_token_spot[(all_token_spot['Instrument']=="EQ") & (all_token_spot['Symbol'].isin(fno_stocks_list))]
    
    underlying_index_token = all_token_spot[all_token_spot['Instrument']=='INDEX']

    # spot_token.reset_index(drop=True, inplace=True)

    # #Future and Option token
    derivative_index_token = all_token_NFO[all_token_NFO['Instrument'].isin(['FUTIDX', 'OPTIDX'])]

    derivative_stock_token = all_token_NFO[(all_token_NFO['Instrument'].isin(['FUTSTK', 'OPTSTK']))
                                           & (all_token_NFO['Symbol'].isin(fno_stocks_list))]


    #############
    #BSE (Sensex Future and Option Token only, Index not found)
    #############
    bse_token_NFO.drop(columns=fno_columns_to_drop, inplace=True)

    sensex_fut_option_tokens = bse_token_NFO[bse_token_NFO['Symbol'].isin(['BSXOPT', 'BSXFUT'])]

    dfs = [underlying_stock_token, underlying_index_token,
           derivative_index_token, derivative_stock_token,
           sensex_fut_option_tokens]

    nse_index_stock_token = pd.concat(dfs, axis=0)
    nse_index_stock_token.reset_index(drop=True, inplace=True)

    # nse_tokens[nse_tokens['Instrument']=='OPTIDX'].Symbol.unique()
    # nse_tokens[nse_tokens['Instrument']=='FUTIDX'].Symbol.unique()
    # nse_tokens[nse_tokens['Instrument']=='INDEX'].Symbol.unique()

    mapping = {
    "Nifty 50": "NIFTY",
    "Nifty Bank": "BANKNIFTY",
    "Nifty Next 50": "NIFTYNXT50",
    "Nifty Fin Services": "FINNIFTY",
    "NIFTY MID SELECT": "MIDCPNIFTY",
    "INDIAVIX": "INDIAVIX"  # no FUTIDX, keep unchanged
    }

    nse_index_stock_token.loc[nse_index_stock_token['Instrument'] == 'INDEX', 'Symbol'] = (
    nse_index_stock_token.loc[nse_index_stock_token['Instrument'] == 'INDEX', 'Symbol']
    .map(mapping)
    )


    # return underlying_index_token, derivative_index_token, underlying_stock_token, derivative_stock_token , all_token_NFO, all_token_spot
    return  all_token_NFO, all_token_spot
    
    # return nse_index_stock_token




def add_token_info(df, stock_df, token):
    '''
    This will add stocks info like symbol, exp_date, option_type, strike_price, instrument etc 
    into data downloaded from shoonya Api
    '''
    #Spliting date and time into saperate columns
    df.rename(columns = {'time':'datetime','into':'open','inth':'high','intl':'low','intc':'close'},inplace=True)
    df['date'] = df['datetime'].apply(lambda x:x.split(" ")[0])
    df['time'] = df['datetime'].apply(lambda x:x.split(" ")[1])

    df['symbol']         = stock_df[stock_df['Token']==token]['Symbol'].iloc[0]
    df['trading_symbol'] = stock_df[stock_df['Token']==token]['TradingSymbol'].iloc[0]
    df['exp_date']       = stock_df[stock_df['Token']==token]['Expiry'].iloc[0]
    df['option_type']    = stock_df[stock_df['Token']==token]['OptionType'].iloc[0]
    df['strike_price']   = stock_df[stock_df['Token']==token]['StrikePrice'].iloc[0]
    df['instrument']     = stock_df[stock_df['Token']==token]['Instrument'].iloc[0]

    df = df[['symbol','date','time','trading_symbol', 'instrument', 'exp_date','option_type','strike_price','open','high','low','close','intvwap','intv','intoi','v','oi','ssboe','stat']]
    return df




def save_csv(save_path: str, df: pd.DataFrame, filename: str, index: bool = False) -> None:
    """
    Save a DataFrame as a CSV file in the given folder.
    Creates the folder if it does not exist.

    Parameters:
    ----------
    save_path : str
        Path to the folder where the file will be saved.
    df : pd.DataFrame
        DataFrame to save.
    filename : str
        Name of the file (with or without .csv extension).
    """
    # Ensure folder exists
    os.makedirs(save_path, exist_ok=True)

    # Ensure filename has .csv extension
    if not filename.lower().endswith(".csv"):
        filename += ".csv"

    # Full path to file
    file_path = os.path.join(save_path, filename)

    # Save dataframe
    df.to_csv(file_path, index=index)
    print(f"File saved at: {file_path}")
