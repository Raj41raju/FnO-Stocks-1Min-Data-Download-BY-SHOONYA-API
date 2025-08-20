# 📊 Data Download Pipeline with Rate Limiting

This project is a **data download pipeline** that connects to the **Finwesiya API** to fetch intraday market data.  
It ensures **rate-limited API requests** (10 per second and 200 per minute) and saves the downloaded data in CSV format.

## Base URL
for URL for Token Download

root ='https://api.shoonya.com/'

host URL(API)

REST API: https://api.shoonya.com/NorenWClientTP/
WebSocket: wss://api.shoonya.com/NorenWSTP/

---

## 🚀 Features

- ✅ **Config file support (`config.json`)** – Store API credentials, paths, and keys separately  
- ✅ **Authentication wrapper** – Handles login/logout with the API  
- ✅ **Rate-limiting control** – Respects API limits (10 requests/sec, 200 requests/min)  
- ✅ **Parallel requests** – Improves speed while staying within rate limits  
- ✅ **Error handling & retries** – Automatic retry for failed requests  
- ✅ **CSV saving** – Saves clean intraday data for each symbol  
- ✅ **Execution time tracking** – Measure performance of downloads  

---

## 📂 Project Structure

```
project/
│── config.json                # Configuration file (paths, credentials, API keys)
│── data_download_pipeline.py  # Main pipeline script
│── requirements.txt           # Python dependencies
│── output/                    # Folder for downloaded CSV files
```

## ⚙️ Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/Raj41raju/FnO-Stocks-1Min-Data-Download-BY-SHOONYA-API
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Update `config.json` with your credentials, API keys, and paths.

## 🚀 Usage

Run the pipeline with:
```bash
python main.py
```

This will:
- Authenticate with the API
- Download FnO data for (Index and Stocks, also included sensex(only sensex))
- Save files in the directory

## 📑 Configuration (`config.json`)

Example config:
```json
{
  "token": "TOTP token key for 2FA",
  "user": "FAxxxxx",
  "password": "xxxxx",
  "vc": "FAxxxx_U",
  "apikey": "xxxxx",
  "imei": "xxxxx"
}
```

## 📌 Requirements

- Python 3.8+
- pandas
- requests
- zipfile36
- logging

Install them via:
```bash
pip install -r requirements.txt
```






## 🔮 Future Scope

- Build visualization dashboard for data insights by Implement Open Interest (OI) change tracking for Call/Put options 
- Future OI Analysis
- 

## 👤 Author

**Raju Kumar Singh**  
_Data Analyst | Algo Trader | Developer_

