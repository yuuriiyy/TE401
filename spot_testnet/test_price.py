import json
import os
import binance_connect
from candlestick_plot import plotCandles

def get_settings(import_path):
    if os.path.exists(import_path):
        file = open(import_path, "r")
        project_settings =  json.load(file)
        file.close()
        return project_settings
    else:
        return ImportError


if __name__ == "__main__":
    # Check System Status and Testnet Status
    status = binance_connect.query_binance_status()
    testnet = binance_connect.query_testnet()

    # Import User Data from 
    json_path = "api_settings.json"
    project_settings = get_settings(json_path)
    api_key = project_settings["BinanceKeys"]["API_Key"]
    secret_key = project_settings["BinanceKeys"]["Secret_Key"]
    # print(api_key)
    # print(secret_key)

    candles_data =  binance_connect.get_candlestick_data("BTCUSDT", "1m", 1)
    print("open: ", candles_data[0]["open"])
    account = binance_connect.query_account(api_key, secret_key)
    print(account['balances'][1])
    print(account['balances'][4])
    # print(account)

    response = binance_connect.query_testnet()
    print(response)

