import pandas as pd
from datetime import date
import os
import requests
import zipfile36 as zipfile
from NorenRestApiPy.NorenApi import  NorenApi
#from threading import Timer
import time
import logging
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
        print(f'downloading {zip_file}')
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
            print("Invalid file")

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
