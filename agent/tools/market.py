import os
from alpha_vantage.timeseries import TimeSeries
import pandas as pd
from dotenv import load_dotenv
import time
import json
from datetime import date

load_dotenv()
api_key = os.getenv("ALPHA_VANTAGE_API_KEY") 
symbols = ['MSFT', 'AAPL', 'GOOGL', 'TSLA', 'IBM']
CACHE_FILE = "data/stock_cache.json"

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    # if the cache file does not exist yet (first time you run the program), return an empty dictionary instead of crashing
    return {}

def save_cache(data:dict):
    with open(CACHE_FILE, "w") as f:
        json.dump(data, f)
        

def tech_stock_price() -> str:
    today = str(date.today())
    cache = load_cache()

    #if the system already fetched and saved today's data
    if cache.get("date") == today:
        print("Using cached stock prices for today.")
        return cache["data"]
    
    # Otherwise fetch the data
    print("Fetching fresh stock prices from Alpha Vantage...")
    time_series = TimeSeries(key=api_key, output_format='pandas')
    result = ""
    for ticker in symbols:
        print(f"Fetching data for {ticker}...")
        try:
            data, _ = time_series.get_daily(ticker)
            month = data.head(30)
            latest_closed = month.iloc[0]['4. close'] # most recent closed day only
            month_ago_closed = month.iloc[-1]['4. close']
            change = latest_closed - month_ago_closed
            change_percentage = (change/month_ago_closed) * 100
            trend = "↑ UP" if change > 0 else "↓ DOWN"
            result += f"{ticker} \n"
            f"Latest Close: {latest_closed} \n"
            f"One-Month Chnage: {change:+.2f} ({change_percentage:+.1f}%) {trend} \n"
            f"One-Month High: {month['2. high'].max()}\n"
            f"One-Month Low: {month['3. low'].min()}\n\n"
            time.sleep(12)
        except Exception as e:
            print(f"Error for {ticker}: {e}")
            result += f"{ticker} — Error fetching data\n"
    save_cache({"date": today, "data": result})
    return result