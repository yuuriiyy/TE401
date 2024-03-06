import hmac
import time
import hashlib
import requests
import sqlite3
import json
import numpy as np
from urllib.parse import urlencode
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
from um_futures import send_public_request, send_signed_request, dispatch_request

# ... (Your existing code for API key setup and request functions)

# SQLite database connection setup
conn = sqlite3.connect('funding_rate_database.db')
cursor = conn.cursor()
symbol = 'BTC'

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
    funding_rate = float(response['lastFundingRate'])
    timestamp = int(response['time'] / 1000)  # Convert milliseconds to seconds

    print(response)
    # save_funding_rate_to_db(symbol, data)
    print(f"Funding rate for {symbol}: {funding_rate} (Timestamp: {timestamp})")

# Fetch and save funding rates for a specific symbol (e.g., 'BTCUSDT')
fetch_and_save_funding_rate('BTCUSDT')

# Function to predict future funding rates using linear regression
# def predict_future_funding_rate(symbol, days=1):
#     # Fetch historical data from the database
#     cursor.execute('''
#         SELECT timestamp, funding_rate
#         FROM funding_rates
#         WHERE symbol = ?
#         ORDER BY timestamp ASC
#     ''', (symbol,))
#     data = cursor.fetchall()

#     # Prepare data for training
#     timestamps = np.array([entry[0] for entry in data]).reshape(-1, 1)
#     funding_rates = np.array([entry[1] for entry in data])

#     # Train linear regression model
#     model = LinearRegression()
#     model.fit(timestamps, funding_rates)

#     # Predict future funding rate
#     future_timestamp = int((datetime.utcnow() + timedelta(days=days)).timestamp())
#     predicted_funding_rate = model.predict([[future_timestamp]])[0]

#     print(f"Predicted funding rate for {symbol} in {days} days: {predicted_funding_rate}")

# # Predict future funding rate for 'BTCUSDT' in 7 days
# predict_future_funding_rate('BTCUSDT', days=7)

# Close the SQLite connection
conn.close()
