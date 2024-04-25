import hmac
import time
import hashlib
import requests
import sqlite3
import json
import logging
import numpy as np
import datetime
from urllib.parse import urlencode
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from um_futures import send_public_request, send_signed_request, dispatch_request


logging.basicConfig(filename='example.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to fetch and save funding rates
def fetch_and_save_funding_rate(symbol):
    response = send_signed_request("GET", "/fapi/v1/premiumIndex", {"symbol": symbol})
    logging.warning("Log app started")
    logging.info(f'{response}')
    print(response)
    # response = send_signed_request("GET", "/fapi/v1/fundingRate", {"symbol": symbol, "limit": 15})
    # print(response)

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
    print(f"time: {response['time']} ,funding rate: {current_funding_rate}")
    if(current_funding_rate > funding_rate_10MA):
        logging.info("signal: True")
        print("signal:", True)
    else:
        logging.info("signal: False")
        print("signal:", False)
    # response = send_signed_request("GET", "/fapi/v1/fundingRate", {"symbol": symbol, "startTime": start, "endTime": end, "limit": limit})
    # print(funding_rates)

while True:
# Fetch and save funding rates for a specific symbol (e.g., 'BTCUSDT')
    # fetch_and_save_funding_rate('BTCUSDT')
    fetch_funding_rate_with_limit('BTCUSDT', limit = 10)
    time.sleep(150)