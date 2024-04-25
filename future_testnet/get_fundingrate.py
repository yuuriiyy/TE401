import hmac
import time
import hashlib
import requests
import sqlite3
import json
import numpy as np
import datetime
from urllib.parse import urlencode
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from um_futures import send_public_request, send_signed_request, dispatch_request

# ... (Your existing code for API key setup and request functions)

# SQLite database connection setup
conn = sqlite3.connect('funding_rate_database.db')
cursor = conn.cursor()
symbol = 'USDT'

# Create a table to store funding rates if not exists
cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {symbol}_funding_rate (
                timestamp INTEGER PRIMARY KEY,
                close_contract REAL,
                close_spot REAL,
                funding_rate REAL
            );
        ''')
conn.commit()

# Function to save funding rate data to SQLite
def save_funding_rate_to_db(symbol, data):
    cursor.executemany(f'''
            INSERT INTO BTC_funding_rate (timestamp, close_contract, close_spot, funding_rate)
            VALUES (?, ?, ?, ?)
        ''', data)
    conn.commit()

# Function to fetch and save funding rates
def fetch_and_save_funding_rate(symbol):
    response = send_signed_request("GET", "/fapi/v1/premiumIndex", {"symbol": symbol})
    # response = send_signed_request("GET", "/fapi/v1/fundingRate", {"symbol": symbol, "limit": 15})
    print(response)

start_date = '2024-03-01'
end_date = '2024-03-02'
start = int(datetime.datetime.strptime(start_date, '%Y-%m-%d').timestamp() * 1000)
end = int(datetime.datetime.strptime(end_date, '%Y-%m-%d').timestamp() * 1000)
def fetch_funding_rate_with_limit(symbol, limit = 10):
    data = send_signed_request("GET", "/fapi/v1/fundingRate", {"symbol": symbol, "limit": limit})
    funding_rates = [float(entry['fundingRate']) for entry in data]
    funding_rate_10MA = sum(funding_rates) / limit
    response = send_signed_request("GET", "/fapi/v1/premiumIndex", {"symbol": symbol})
    current_funding_rate = float(response["lastFundingRate"])
    if(current_funding_rate > funding_rate_10MA):
        print(True)
    else:
        print(False)
    # response = send_signed_request("GET", "/fapi/v1/fundingRate", {"symbol": symbol, "startTime": start, "endTime": end, "limit": limit})
    # print(funding_rates)


# Fetch and save funding rates for a specific symbol (e.g., 'BTCUSDT')
# fetch_and_save_funding_rate('BTCUSDT')
fetch_funding_rate_with_limit('BTCUSDT', limit = 10)

conn.close()
