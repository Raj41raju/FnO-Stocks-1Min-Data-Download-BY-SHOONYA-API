# 📊 Data Download Pipeline with Rate Limiting

This project is a **data download pipeline** that connects to the **Finwesiya API** to fetch intraday market data.  
It ensures **rate-limited API requests** (20 per second and 200 per minute) and saves the downloaded data in CSV format.

---
### **Note :** Here i skip the 1Min API Rate Limit and it is working properly.

## Base URL
for URL for Token Download

root ='https://api.shoonya.com/'

host URL(API)

REST API: https://api.shoonya.com/NorenWClientTP/
WebSocket: wss://api.shoonya.com/NorenWSTP/

---

## 🚀 Features
- Connects securely to the **Finwesiya API**.
- Handles **parallel requests** with proper **rate limiting**.
- Saves intraday data in structured **CSV files**.
- Logs errors and execution details for monitoring.
- Configurable via `config.json` for credentials and file paths.

---

## 📂 Project Structure

```
project/
│── config.json                # Configuration file (paths, credentials, API keys)
│── data_download_pipeline.py  # Main pipeline script
│── requirements.txt           # Python dependencies
│── data_validation.py         # Chek the downloaded data 
|── login_test.py              # Check the login credintial
|── data\                      # store sample i/o data
```

## ⚙️ Setup

1. Clone the repository:
   ```bash
   git clone <https://github.com/Raj41raju/FnO-Stocks-1Min-Data-Download-BY-SHOONYA-API/tree/main>
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

## 🚀 Features

- ✅ **Config file support (`config.json`)** – Store API credentials, paths, and keys separately  
- ✅ **Authentication wrapper** – Handles login/logout with the API  
- ✅ **Rate-limiting control** – Respects API limits (10 requests/sec, 200 requests/min)  
- ✅ **Parallel requests** – Improves speed while staying within rate limits  
- ✅ **Error handling & retries** – Automatic retry for failed requests  
- ✅ **CSV saving** – Saves clean intraday data for each symbol  
- ✅ **Execution time tracking** – Measure performance of downloads  


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
## 🚀 Example
#### **🔍 Example 1:** Download Full Data

To **download** all symbols and all tokens for the **given day**, run command:
```bash
python main.py

```

#### **🔍 Example 2:** Testing with Limited Iterations

When trying out **new code changes**, it’s better to limit iterations so you don’t wait hours or overwhelm the API.

#### 2.1  Limit symbols

Change the symbol loop to only take the first one:

```python
for symbol in nse_tokens.Symbol.unique()[:1]:  
   # Download data for only one symbol

```

#### 2.2 Limit tokens

Change the token loop to only take first 10 tokens:
```python
for token in temp_stock_df['Token'].unique()[:10]:  
    # Download data for only 10 tokens

```

✅ This way, you can quickly check whether:

- File saving works
- API response is correct
- Data format looks fine
- Correct format of data save to folder

## 🔮 Future Scope

- Automate it to download all the data daily at 11PM when Exchange is not closed.
- Generate Automatic report daily if any stocks and index.
- Build visualization dashboard for data insights by Implement Open Interest (OI) change tracking for Call/Put options 
- Future OI Analysis

## 👤 Author

**Raju Kumar Singh**  
_Data Analyst | Algo Trader | Developer_

