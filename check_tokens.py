import pandas as pd
import numpy as np

from data_download_pipeline import token_download, token_formating
import time 
import os 

def all_tokens(token_save_path):

    # Token folder (daily)
    current_date = time.strftime('%Y-%m-%d', time.localtime())
    token_path = os.path.join(token_save_path, current_date)
    os.makedirs(token_path, exist_ok=True)

    # Download tokens if not already
    token_download(token_path)

    nse_tokens = token_formating(token_path)
    return nse_tokens

token_save_path = "C:\\Finvasia_API_Code\\Token_intraday"
tokens = all_tokens(token_save_path)