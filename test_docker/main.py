import time
import logging
import numpy as np
import os
import pathlib
from configparser import ConfigParser
from urllib.parse import urlencode

from binance.spot import Spot as Client
from binance.error import ClientError
from binance.lib.utils import config_logging

from apiHandler import FutureAPIHandler, SpotAPIHandler

import schedule



# logging.basicConfig(filename='example.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')



def get_api_key(type):
    config = ConfigParser()
    config_file_path = os.path.join(
        pathlib.Path(__file__).parent.resolve(),  "config.ini"
    )
    config.read(config_file_path)
    return config[type+"_keys"]["api_key"], config[type+"_keys"]["api_secret"]


# Function to fetch and save funding rates
def fetch_and_save_funding_rate(symbol):
    # initialize the handler
    api_key, api_secret = get_api_key("spot")
    BASE_URL = "https://testnet.binancefuture.com"  # testnet base url
    handler = FutureAPIHandler(BASE_URL, api_key, api_secret)

    response = handler.send_signed_request("GET", "/fapi/v1/premiumIndex", {"symbol": symbol})
    logging.info(f'{response}')


def spot_order(side):
    # side = "BUY" or "SELL"
    api_key, api_secret = get_api_key("spot")
    handler = SpotAPIHandler(api_key=api_key, secret_key=api_secret)
    account = handler.query_account()
    logging.info(account['balances'][1])
    logging.info(account['balances'][4])


    # get current BTCUSDT price
    candles_data =  handler.get_candlestick_data("BTCUSDT", "1m", 1)
    logging.info("current price: ", candles_data[0]["open"])
    current_price = float(candles_data[0]["open"])
    
    # buy / sell the spot
    client = Client(
        api_key=api_key,
        api_secret=api_secret,
        base_url="https://testnet.binance.vision",
    )
    info = client.exchange_info(symbol="BTCUSDT")
    data = info["symbols"][0]
    params = {
    "symbol": "BTCUSDT",
    "side": side,
    "type": "LIMIT",
    "timeInForce": "GTC",
    "quantity": 0.01,
    "price": current_price, ### set the price to current price
    }

    try:
        logging.info(f"transaction: {side}ing")
        response = client.new_order(**params)
        logging.info(response)
    except ClientError as error:
        logging.error(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )

    # check current account information after transaction
    account = handler.query_account()
    logging.info(account['balances'][1])
    logging.info(account['balances'][4])


def future_order(side):
    # get api key and secret
    api_key, api_secret = get_api_key("spot")

    BASE_URL = "https://testnet.binancefuture.com"  # testnet base url
    handler = FutureAPIHandler(BASE_URL, api_key, api_secret) # initial request handler

    # get account information
    account = handler.send_signed_request("GET", "/fapi/v2/account")
    logging.info(account)

    # get current price
    premiumIndex = handler.send_signed_request("GET", "/fapi/v1/premiumIndex",{"symbol": "BTCUSDT"})
    logging.info("lastFundingRate", premiumIndex["lastFundingRate"])
    logging.info("indexPrice", premiumIndex["indexPrice"])
    current_price  = round(float(premiumIndex["indexPrice"]), 0)

    # buy or sell the future
    params = {
        "symbol": "BTCUSDT",
        "side": side,
        "type": "LIMIT",
        "timeInForce": "GTC",
        "quantity": 0.01,
        "price": current_price,
    }
    logging.info(f"transaction: {side}ing")

    response = handler.send_signed_request("POST", "/fapi/v1/order", params)
    logging.info(response)


def fetch_funding_rate_with_limit(symbol, limit = 10):
    # initialize the handler
    api_key, api_secret = get_api_key("spot")
    BASE_URL = "https://testnet.binancefuture.com"  # testnet base url
    handler = FutureAPIHandler(BASE_URL, api_key, api_secret)

    # get funding rate and calculate the signal
    data = handler.send_signed_request("GET", "/fapi/v1/fundingRate", {"symbol": symbol, "limit": limit})
    funding_rates = [float(entry['fundingRate']) for entry in data]
    funding_rate_10MA = sum(funding_rates) / limit
    response = handler.send_signed_request("GET", "/fapi/v1/premiumIndex", {"symbol": symbol})
    current_funding_rate = float(response["lastFundingRate"])
    logging.info(f"time: {response['time']} ,funding rate: {current_funding_rate}")
    # print(f"time: {response['time']} ,funding rate: {current_funding_rate}")

    # transaction
    if(current_funding_rate > funding_rate_10MA):
        logging.info("signal: True")
        # print("signal:", True)
        # spot_order("BUY")
        future_order("SELL")

    else:
        logging.info("signal: False")
        # print("signal:", False)
        # spot_order("SELL")
        # future_order("BUY")


    # response = send_signed_request("GET", "/fapi/v1/fundingRate", {"symbol": symbol, "startTime": start, "endTime": end, "limit": limit})
    # print(funding_rates)

if __name__ == "__main__":
    # Fetch and save funding rates for a specific symbol (e.g., 'BTCUSDT')
    # fetch_funding_rate_with_limit('BTCUSDT', limit = 10)

    
    def job():
        fetch_funding_rate_with_limit('BTCUSDT', limit = 10)

    schedule.every(8).hours.do(job)
    while True:
        schedule.run_pending()
        time.sleep(1)