import time
import logging
from binance.lib.utils import config_logging
from binance.spot import Spot as Client
from binance.websocket.spot.websocket_stream import SpotWebsocketStreamClient
from binance.websocket.spot.websocket_api import SpotWebsocketAPIClient
from prepare_env import get_api_key

api_key, api_secret = get_api_key()

config_logging(logging, logging.DEBUG)


def on_close(_):
    logging.info("Do custom stuff when connection is closed")


def message_handler(_, message):
    logging.info(message)


my_client = SpotWebsocketAPIClient(
    stream_url="wss://fstream.binancefuture.com",
    api_key=api_key,
    api_secret=api_secret,
    on_message=message_handler,
    on_close=on_close,
)

# my_client.account()
my_client.new_order(
    id=12345678,
    symbol="BTCUSDT",
    side="BUY",
    type="LIMIT",
    timeInForce="GTC",
    quantity=0.01,
    price=52097,
    newClientOrderId="my_order_id_1",
    newOrderRespType="RESULT",
)

time.sleep(2)

logging.info("closing ws connection")
my_client.stop()