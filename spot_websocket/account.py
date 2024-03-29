#!/usr/bin/env python

import logging
import time
import json
import sys
sys.path.insert(0, '..')
from binance.lib.utils import config_logging
from binance.websocket.spot.websocket_api import SpotWebsocketAPIClient
from prepare_env import get_api_key

api_key, api_secret = get_api_key()

config_logging(logging, logging.DEBUG)


def on_close(_):
    logging.info("Do custom stuff when connection is closed")


def message_handler(_, message):
    msg = json.loads(message)
    print(msg["result"]["balances"][0]) #ETH
    print(msg["result"]["balances"][1]) #BTC
    print(msg["result"]["balances"][4]) #USDT

    # logging.info(message)


my_client = SpotWebsocketAPIClient(
    stream_url="wss://testnet.binance.vision/ws-api/v3",
    api_key=api_key,
    api_secret=api_secret,
    on_message=message_handler,
    on_close=on_close,
)


my_client.account()

time.sleep(2)

logging.info("closing ws connection")
my_client.stop()