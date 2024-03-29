#!/usr/bin/env python

import logging
import time
import sys
sys.path.insert(0, '..')
from binance.lib.utils import config_logging
from binance.websocket.spot.websocket_api import SpotWebsocketAPIClient

config_logging(logging, logging.DEBUG)


def on_close(_):
    logging.info("Do custom stuff when connection is closed")


def message_handler(_, message):
    logging.info(message)


my_client = SpotWebsocketAPIClient(on_message=message_handler, on_close=on_close)


my_client.avg_price(symbol="ETHUSDT")

time.sleep(2)

logging.info("closing ws connection")
my_client.stop()