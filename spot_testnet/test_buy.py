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


def filters(client):
    info = client.exchange_info(symbol="BTCUSDT")
    data = info["symbols"][0]
    # print(info["symbols"][0]["filters"])
    # print(info["symbols"][0])


    # Ectract filters
    price_filter = data["filters"][0]  # Assuming price filter is at index 0
    lot_size_filter = data["filters"][1] # Assuming lot size filter is at index 1
    percent_price_by_side = data["filters"][5]
    notional = data["filters"][6]

    # Extract required values
    min_price = float(price_filter["minPrice"])
    max_price = float(price_filter["maxPrice"])
    tick_size = float(price_filter["tickSize"])
    print("min_price, max_price, tick_size: ",min_price, max_price, tick_size)

    min_qty = float(lot_size_filter["minQty"])
    max_qty = float(lot_size_filter["maxQty"])
    # print("min_qty, max_qty: ", min_qty, max_qty)

    weighted_average_price = float(percent_price_by_side["bidMultiplierUp"])
    multiplier_up = float(percent_price_by_side["bidMultiplierUp"])
    multiplier_down = float(percent_price_by_side["bidMultiplierDown"])
    bid_multiplier_up = float(percent_price_by_side["bidMultiplierUp"])
    bid_multiplier_down = float(percent_price_by_side["bidMultiplierDown"])

    min_notional = float(notional["minNotional"])
    max_notional = float(notional["maxNotional"])
    # print("min_notional, max_notional: ", min_notional, max_notional)

    price_up =  weighted_average_price * min(multiplier_up, bid_multiplier_up, max_price)
    price_down = weighted_average_price * max(multiplier_down, bid_multiplier_down, min_price)
    price = (price_up + price_down) / 2
    # print("price_up, price_down, price: ", price_up, price_down, price)


if __name__ == "__main__":

    json_path = "api_settings.json"
    project_settings = get_settings(json_path)
    api_key = project_settings["BinanceKeys"]["API_Key"]
    api_secret = project_settings["BinanceKeys"]["Secret_Key"]

    account = binance_connect.query_account(api_key, api_secret)
    print(account['balances'][1])
    print(account['balances'][4])
    
    client = Client(
        api_key=api_key,
        api_secret=api_secret,
        base_url="https://testnet.binance.vision",
    )
    candles_data =  binance_connect.get_candlestick_data("BTCUSDT", "1m", 1)
    print("current price: ", candles_data[0]["open"])
    price = float(candles_data[0]["open"])

    info = client.exchange_info(symbol="BTCUSDT")
    data = info["symbols"][0]
    params = {
    "symbol": "BTCUSDT",
    "side": "BUY",
    "type": "LIMIT",
    "timeInForce": "GTC",
    "quantity": 0.02,
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

    # print(account['balances'][0])
    print(account['balances'][1])
    print(account['balances'][4])

    

    
"""
price >= minPrice
price <= maxPrice
price % tickSize == 0


## PERCENT_PRICE
- price <= weightedAveragePrice * multiplierUp
- price >= weightedAveragePrice * multiplierDown

## PERCENT_PRICE_BY_SIDE
Buy : 
- price <= weightedAveragePrice * multiplierUp
- price >= weightedAveragePrice * multiplierDown
Sell:
- Order Price <= weightedAveragePrice * askMultiplierUp
- Order Price >= weightedAveragePrice * askMultiplierDown


quantity >= minQty
quantity <= maxQty
quantity % stepSize == 0

price * quantity <= maxNotional
price * quantity >= minNotional
"""
