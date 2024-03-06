#!/usr/bin/env python

import logging
import time
import json
import sys
sys.path.insert(0, '..')
from binance.lib.utils import config_logging
from binance.websocket.spot.websocket_api import SpotWebsocketAPIClient

config_logging(logging, logging.DEBUG)


def on_close(_):
    pass
    logging.info("Do custom stuff when connection is closed")


def message_handler(_, message):
    '''
    message =  {
    "id":"5ec96722-6c58-4053-b397-166e60927f77",
    "status":200,
    "result":{"mins":5,"price":"251.80255911","closeTime":1702609187409},
    "rateLimits":[{"rateLimitType":"REQUEST_WEIGHT","interval":"MINUTE","intervalNum":1,"limit":6000,"count":4}]
    }
    '''
    msg = json.loads(message)
    print(msg["result"])
    # logging.info(msg["result"])


if __name__ == '__main__':

    my_client = SpotWebsocketAPIClient(on_message=message_handler, on_close=on_close)
    for i in range(100):
        my_client.ticker_price(symbol="BTCUSDT")
        time.sleep(1)

    # time.sleep(20)
    # my_client.ticker_price(symbols=["BNBBUSD", "BTCUSDT"])
    # time.sleep(2)

    logging.info("closing ws connection")
    my_client.stop()