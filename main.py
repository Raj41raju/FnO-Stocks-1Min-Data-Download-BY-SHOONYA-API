
import pandas as pd
from datetime import date
import os
import requests
import time
import zipfile36 as zipfile
import logging
import warnings
warnings.filterwarnings('ignore')

print(os.getcwd())

from data_download_pipeline import data_download

start_timestamp = "19-08-2025 09:15:00"
end_timestamp = "19-08-2025 15:30:00"
token_save_path = "C:\\Finvasia_API_Code\\Token_intraday"
save_path = "C:\\DATA\\Finvasia Data\\Stock_FnO"

data_download(
   save_path,
   token_save_path,
   start_timestamp,
   end_timestamp,
)