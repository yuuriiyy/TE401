import logging
import os
import json
import binance_connect
from binance.spot import Spot as Client
from binance.error import ClientError
from binance.lib.utils import config_logging
from binance.error import ParameterRequiredError


def get_settings(import_path):
    if os.path.exists(import_path):
        file = open(import_path, "r")
        project_settings =  json.load(file)
        file.close()
        return project_settings
    else:
        return ImportError


def test_account_snapshot(client, mock_item):
    """Tests the API endpoint to get account snapshot"""
    response = client.account_snapshot(type="SPOT")
    response.should.equal(mock_item)


def test_account_snapshot_without_type(client):
    """Tests the API endpoint to get account snapshot without type"""
    client.account_snapshot.when.called_with("").should.throw(ParameterRequiredError)


def spot_order(side):
    # side = "BUY" or "SELL"
    json_path = "api_settings.json"
    project_settings = get_settings(json_path)
    api_key = project_settings["BinanceKeys"]["API_Key"]
    api_secret = project_settings["BinanceKeys"]["Secret_Key"]

    # get current account information
    account = binance_connect.query_account(api_key, api_secret)
    print(account['balances'][1])
    print(account['balances'][4])

    # get current BTCUSDT price
    candles_data =  binance_connect.get_candlestick_data("BTCUSDT", "1m", 1)
    print("current price: ", candles_data[0]["open"])
    price = float(candles_data[0]["open"])

    # buy the spot
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
    "price": price, ### set the price to current price
    }

    try:
        print("buying")
        response = client.new_order(**params)
        logging.info(response)
    except ClientError as error:
        logging.error(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )

    # get current account information
    account = binance_connect.query_account(api_key, api_secret)
    print(account['balances'][1])
    print(account['balances'][4])




if __name__ == "__main__":
    spot_order("BUY")


    # json_path = "api_settings.json"
    # project_settings = get_settings(json_path)
    # api_key = project_settings["BinanceKeys"]["API_Key"]
    # api_secret = project_settings["BinanceKeys"]["Secret_Key"]

    # # get current account information
    # account = binance_connect.query_account(api_key, api_secret)
    # print(account['balances'][1])
    # print(account['balances'][4])

    # # get current BTCUSDT price
    # candles_data =  binance_connect.get_candlestick_data("BTCUSDT", "1m", 1)
    # print("current price: ", candles_data[0]["open"])
    # price = float(candles_data[0]["open"])

    # # buy the spot
    # client = Client(
    #     api_key=api_key,
    #     api_secret=api_secret,
    #     base_url="https://testnet.binance.vision",
    # )
    # info = client.exchange_info(symbol="BTCUSDT")
    # data = info["symbols"][0]
    # params = {
    # "symbol": "BTCUSDT",
    # "side": "BUY",
    # "type": "LIMIT",
    # "timeInForce": "GTC",
    # "quantity": 0.01,
    # "price": price, ### set the price to current price
    # }

    # try:
    #     print("buying")
    #     response = client.new_order(**params)
    #     logging.info(response)
    # except ClientError as error:
    #     logging.error(
    #         "Found error. status: {}, error code: {}, error message: {}".format(
    #             error.status_code, error.error_code, error.error_message
    #         )
    #     )

    # print(account['balances'][0])
    # print(account['balances'][1])
    # print(account['balances'][4])
