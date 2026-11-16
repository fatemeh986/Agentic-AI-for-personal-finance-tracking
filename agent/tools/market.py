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
    rows = []          # one dict per stock that downloaded successfully
    failed = []        # tickers that could not be fetched
    for ticker in symbols:
        print(f"Fetching data for {ticker}...")
        try:
            data, _ = time_series.get_daily(ticker)
            # Rows are trading days (no weekends/holidays): ~21 trading days = 1 calendar month
            month = data.head(21)
            latest_closed = month.iloc[0]['4. close'] # most recent closed day only
            month_ago_closed = month.iloc[-1]['4. close']
            change = latest_closed - month_ago_closed
            change_percentage = (change/month_ago_closed) * 100
            trend = "↑ UP" if change > 0 else "↓ DOWN"
            # Step 1: only COLLECT the numbers here, don't build the text yet
            rows.append({
                "ticker": ticker,
                "close": latest_closed,
                "change": change,
                "pct": change_percentage,
                "trend": trend,
                "high": month['2. high'].max(),
                "low": month['3. low'].min(),
            })
        except Exception as e:
            print(f"Error for {ticker}: {e}")
            failed.append(ticker)
        time.sleep(12)  # Alpha Vantage free tier: max 5 requests per minute

    if not rows:
        return "Error: stock data is not available right now."

    # Step 2: let PYTHON compare the numbers (LLMs are unreliable at this)
    rows.sort(key=lambda r: r["pct"], reverse=True)   # best performer first
    best, worst = rows[0], rows[-1]

    # Step 3: build the text, with the answer to "which is best/worst" at the top
    # (the parentheses make Python join all these f-strings into ONE string)
    result = (
        f"Best performer: {best['ticker']} ({best['pct']:+.1f}%) | "
        f"Worst performer: {worst['ticker']} ({worst['pct']:+.1f}%)\n"
        "Sorted by one-month change, best to worst:\n\n"
    )
    for r in rows:
        result += (
            f"{r['ticker']}\n"
            f"Latest Close: {r['close']}\n"
            f"One-Month Change: {r['change']:+.2f} ({r['pct']:+.1f}%) {r['trend']}\n"
            f"One-Month High: {r['high']}\n"
            f"One-Month Low: {r['low']}\n\n"
        )
    for ticker in failed:
        result += f"{ticker} — Error fetching data\n"

    # Only cache a complete result; otherwise a temporary error would be reused all day
    if not failed:
        save_cache({"date": today, "data": result})
    return result