
import pandas as pd
from datetime import date
import os
import requests
import time
import zipfile36 as zipfile
import warnings
warnings.filterwarnings('ignore')
# import modules
from modules import token_download, ShoonyaApiLogin, get_time, add_token_info

# Get the current local time as a struct_time object
local_time = time.localtime()
# Format the current date as a string
current_date = time.strftime('%Y-%m-%d', local_time)
#Function call to download token file and save it to saperate directory mention in path
path = f"E:\\FnO_Stocks_Intraday_data\\token_old\\{current_date}"
token_download(path)

api = ShoonyaApiLogin(token = '57DF444TKFWU347YY55N44IRGMALZXA2',
    user    = 'FA25376',
    pwd     = 'RAJU@88raju',
    vc      = 'FA25376_U',
    app_key = '7f0dca9da87909a1bc35373f68162d42'
)

############# TOKEN Extraction Block
'''
Extracting Spot, option and future token for all Future and Option stocks
'''
#reading spot token file
##'E:\\FnO_Stocks_Intraday_data_download\\token
all_token_spot = pd.read_csv(path + '\\NSE_symbols.txt')

all_token_NFO = pd.read_csv(path + '\\NFO_symbols.txt')

#Future and Options Stocks list
fno_stocks_list = list(all_token_NFO[all_token_NFO['Instrument']=='OPTSTK'].Symbol.unique())

spot_token = all_token_spot[all_token_spot['Instrument']=="EQ"]
spot_token = spot_token[spot_token['Symbol'].isin(fno_stocks_list)]

#Adding empty column to match the all columns name in future and option dataframe
#so that we can concat all the dataframe
spot_token['Expiry'] = 'NaN'
spot_token['OptionType'] = 'NaN'
spot_token['StrikePrice'] = 'NaN'

spot_token.rename(columns = {'Unnamed: 7':'Unnamed: 10'},inplace = True) # for matching column name in future and option 

#Re-arranging the columns name for matching in future and option dataframe
spot_token = spot_token[['Exchange', 'Token', 'LotSize', 'Symbol', 'TradingSymbol', 'Expiry',
       'Instrument', 'OptionType', 'StrikePrice', 'TickSize', 'Unnamed: 10']]
spot_token.reset_index(drop=True, inplace=True)

#Future and Option token
stock_fno_token = all_token_NFO[all_token_NFO['Instrument'].isin(['FUTSTK', 'OPTSTK'])]
print(len(stock_fno_token))
stock_fno_token = stock_fno_token[stock_fno_token['Symbol'].isin(fno_stocks_list)]
print(len(stock_fno_token))

# print(stock_fno_token['Symbol'].nunique())
stock_fno_token.reset_index(drop=True, inplace=True)
#merge both dataframe 
all_stk_token = pd.concat([spot_token, stock_fno_token], ignore_index=True)
all_stk_token.reset_index(drop=True, inplace=True)

##########   DATA Downloading Block


final_columns_list = ['symbol','date','time','trading_symbol', 'instrument', 'exp_date',\
                       'option_type','strike_price','open','high','low','close','intvwap',\
                        'intv','intoi','v','oi','ssboe','stat']


start_time = get_time("22-07-2024 09:15:00")
end_time = get_time("26-07-2024 15:30:00")

for stock in fno_stocks_list[:5]:
    # print(stock)
    temp_stock_df = all_stk_token[all_stk_token['Symbol']==stock]
    # print(temp_df['Instrument'].unique(), len(temp_df)) 

    #Creating an dataframe to store final output
    final_data_df = pd.DataFrame(columns=final_columns_list)

    for token in temp_stock_df['Token'].unique()[:50]:
      temp_token_df = temp_stock_df[temp_stock_df['Token']==token]
      print(temp_token_df.columns)
      # print(temp_token_df)
      token = temp_token_df['Token'].iloc[0]
      exch = temp_token_df['Exchange'].iloc[0]
      print(stock, token, exch)

      if api:
         ret = api.get_time_price_series(exchange=exch, token=str(token), starttime=start_time, endtime=end_time, interval=1)
      if ret:
        data_temp_df = pd.DataFrame.from_dict(ret)
        data_df = add_token_info(data_temp_df, temp_token_df, token)
        final_data_df = pd.concat([final_data_df, data_df])
      # break
    filename = stock + '_' + final_data_df['date'].iloc[0] + '.csv'
    final_data_df.to_csv('E:\\FnO_Stocks_Intraday_data\\' + filename, header=True,index = False )
    # break


    

