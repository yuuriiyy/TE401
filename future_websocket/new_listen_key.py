import logging
from prepare_env import get_api_key
from binance.spot import Spot as Client
from binance.lib.utils import config_logging

config_logging(logging, logging.DEBUG)

api_key, _ = get_api_key()

client = Client(api_key, base_url="https://testnet.binance.vision")
logging.info(client.new_listen_key())