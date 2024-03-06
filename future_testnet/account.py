#!/usr/bin/env python

import time
import logging
from binance.lib.utils import config_logging
from binance.um_futures import UMFutures
from binance.websocket.cm_futures.websocket_client import CMFuturesWebsocketClient
from prepare_env import get_api_key


config_logging(logging, logging.DEBUG)
api_key, api_secret = get_api_key()


def message_handler(_, message):
    print(message)


# api_key = "3a6cf333833b537c783828b8037be85ad9a30c5a77f2d2005081c94c960945ba"
# client = UMFutures(api_key)
client = UMFutures(key = api_key, secret = api_secret)
client.API_URL = 'https://testnet.binancefuture.com'
response = client.new_listen_key()

logging.info("Listen key : {}".format(response["listenKey"]))

ws_client = CMFuturesWebsocketClient(on_message=message_handler)

ws_client.user_data(
    listen_key=response["listenKey"],
    id=1,
)

time.sleep(30)

logging.debug("closing ws connection")
ws_client.stop()