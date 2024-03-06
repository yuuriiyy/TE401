#!/usr/bin/env python

import time
import threading
import logging
import json
import matplotlib.pyplot as plt
from datetime import datetime
from binance.lib.utils import config_logging
from binance.websocket.cm_futures.websocket_client import CMFuturesWebsocketClient

config_logging(logging, logging.DEBUG)


timestamps = []
open_prices = []
close_prices = []
high_prices = []
low_prices = []
volumes = []
def message_handler(_, message):
    message = json.loads(message)
    kline_data = message['k']
    timestamps.append(kline_data['t'])
    open_prices.append(float(kline_data['o']))
    close_prices.append(float(kline_data['c']))
    high_prices.append(float(kline_data['h']))
    low_prices.append(float(kline_data['l']))
    volumes.append(float(kline_data['v']))

    # Print Kline data
    print(f"Timestamp: {kline_data['t']}, Open: {kline_data['o']}, Close: {kline_data['c']}, High: {kline_data['h']}, Low: {kline_data['l']}, Volume: {kline_data['v']}")




my_client = CMFuturesWebsocketClient(on_message=message_handler)

my_client.continuous_kline(
    pair="btcusd",
    id=1,
    contractType="perpetual",
    interval="1m",
)

time.sleep(20)

logging.debug("closing ws connection")
my_client.stop()
