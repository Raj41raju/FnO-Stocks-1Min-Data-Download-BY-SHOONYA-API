from NorenRestApiPy.NorenApi import  NorenApi
#from threading import Timer
import time
import logging
import pyotp
import pandas as pd
import matplotlib.pyplot as plt 


api = None

#Function for time cal
##################################################################################
def get_time(time_string):
    data = time.strptime(time_string,'%d-%m-%Y %H:%M:%S')

    return time.mktime(data)
##################################################################################

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

token = '57DF444TKFWU347YY55N44IRGMALZXA2' 
user    = 'FA25376'
pwd     = 'RAJU@raju88'
factor2 = pyotp.TOTP(token).now()
vc      = 'FA25376_U'
app_key = '7f0dca9da87909a1bc35373f68162d42'
imei    = 'abc1234'

#make the api call
ret = api.login(userid=user, password=pwd, twoFA=factor2, vendor_code=vc, api_secret=app_key, imei=imei)
# df = pd.DataFrame.from_dict(ret)
print(ret)

# start_time = get_time("18-08-2025 09:15:00")
# end_time = get_time("18-08-2025 15:30:00")
# nifty_token = 26000
# banknifty_token = 26009
# indiaVIX_token = 26017
# ret = api.get_time_price_series(exchange="NSE", token=str(indiaVIX_token), starttime=start_time, endtime=end_time, interval=1)
# if ret:
#     data_temp_df = pd.DataFrame.from_dict(ret)
#     # data_df = add_token_info(data_temp_df, temp_token_df, token)
#     # final_data_df = pd.concat([final_data_df, data_df])
# else:
#     print("No data found")


start_time = get_time("19-08-2025 09:15:00")
end_time = get_time("19-08-2025 15:30:00")
token = 826719 #500002 #827334 #132446 #48953
banknifty_token = 26009
indiaVIX_token = 26017
ret = api.get_time_price_series(exchange="BFO", token=str(token), starttime=start_time, endtime=end_time, interval=1)
if ret:
    data_temp_df = pd.DataFrame.from_dict(ret)
    # data_df = add_token_info(data_temp_df, temp_token_df, token)
    # final_data_df = pd.concat([final_data_df, data_df])
else:
    print("No data found")

plt.plot(data_temp_df['time'] , data_temp_df['intc'])
plt.show()

# ret =api.get_daily_price_series(exchange="NSE",tradingsymbol="PAYTM-EQ",startdate="457401600",enddate="480556800")
# ret =api.get_daily_price_series(exchange="NSE",tradingsymbol="ACC-EQ",startdate=start_time,enddate=end_time)

# if ret:
#     data_temp_df = pd.DataFrame.from_dict(ret)
#     # data_df = add_token_info(data_temp_df, temp_token_df, token)
#     # final_data_df = pd.concat([final_data_df, data_df])
# else:
#     print("No data found")


# api.get_security_info(exchange='NSE', token='22')

token_df = pd.read_csv('NFO_symbols.txt')

# token_df[(token_df['Symbol']=='NIFTY') & (token_df['StrikePrice']==25000.0)].sort_values(by='Expiry', ascending=False)

token_df[(token_df['Symbol']=='RELIANCE') & (token_df['StrikePrice']==1400.0)].sort_values(by='Expiry', ascending=False)
