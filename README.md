
# FnO Stocks 1Min Data Download by Shoonya API

The project aims to gather and store 1-minute interval data of Spot, Future, and Option for all FnO Stocks. This data is crucial for traders, analysts, and financial institutions seeking to perform detailed market analysis, backtesting trading strategies, and making informed trading decisions.

## Objectives
### Data Acquisition: 
Automate the download of 1-minute interval data for FnO stocks from a reliable financial data API.

### Data Storage: 
Store the collected data in a structured format suitable for analysis and retrieval.
### Error Handling: 
Implement robust error handling to ensure the reliability and accuracy of the data collection process.
### Scalability: 
Design the system to handle a large volume of data efficiently, ensuring scalability for future data needs.


## API Reference: Shoonya Financial Data API

## Overview
The Shoonya Financial Data API is a comprehensive tool designed to provide high-frequency financial data for Futures and Options (FnO) stocks. 

This API facilitates the collection of data for different intervals like 1Min, 5Min, 15Min, 60Min, 1Day (Daily) weekly, monthly etc. for Spot prices, Future contracts, and Option contracts. 

This documentation provides a detailed reference for using the Shoonya API, including authentication, endpoint details, request parameters, and response formats.

## Base URL
for URL for Token Download

root ='https://api.shoonya.com/'

host URL(API)

REST API: https://api.shoonya.com/NorenWClientTP/
WebSocket: wss://api.shoonya.com/NorenWSTP/

## Authentication
To access the Shoonya API, we must have to authenticate using required credentials and a two-factor authentication (2FA) token. The login endpoint requires the following parameters:

userid: Your user ID.

password: Your password.

twoFA: pyotp.TOTP(token).now() The 2FA code generated using the provided token.

vendor_code: Your vendor code. 

api_secret: Your API secret key.

imei: "abc1234" A unique identifier for your device (optional) common for all

## Endpoints
1. Get Time Price Series
Retrieves 1-minute interval data for a specific stock.

Endpoint: /get_time_price_series
Method: POST

Request Parameters

exchange: The exchange code (e.g., NSE).

token: The token for the stock.

starttime: Start time in Unix timestamp format.

endtime: End time in Unix timestamp format.

interval: Data interval (in minutes).

## Error Handling

When Api faild to login this code (ret = api.login(userid=user, password=pwd, twoFA=factor2, vendor_code=vc, api_secret=app_key, imei=imei))
return None 

And on login success we will get o/p and ret.get('stat') will return "ok"

The API responses include a stat field indicating the status of the request. Common values include:

Ok: The request was successful.
Not_Ok: There was an error with the request.
For unsuccessful requests, an emsg field provides a descriptive error message.


