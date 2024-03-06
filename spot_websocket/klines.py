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
    '''
    message = {
    "id":"b7cccbd6-8d0b-4296-b9d8-bfa4730d67f5",
    "status":200,
    "result":[[1702609080000,"251.90000000","251.90000000","251.90000000","251.90000000","0.00000000",1702609139999,"0.00000000",0,"0.00000000","0.00000000","0"],
    [1702609140000,"251.80000000","251.80000000","251.70000000","251.80000000","9.02200000",1702609199999,"2271.33960000",13,"8.81500000","2219.21700000","0"]],
    "rateLimits":[{"rateLimitType":"REQUEST_WEIGHT","interval":"MINUTE","intervalNum":1,"limit":6000,"count":4}]}
    

    '''
    
    logging.info(message)


my_client = SpotWebsocketAPIClient(on_message=message_handler, on_close=on_close)


#### limit = number of message["results"]
for i in range(100):
    my_client.klines(symbol="BNBBUSD", interval="1m", limit=1)
    time.sleep(2)

logging.info("closing ws connection")
my_client.stop()