import hmac
import time
import hashlib
import requests
from binance.spot import Spot
from urllib.parse import urlencode


class FutureAPIHandler:
    def __init__(self, base_url, key, secret):
        self.BASE_URL = base_url
        self.KEY = key
        self.SECRET = secret

    def hashing(self, query_string):
        return hmac.new(
            self.SECRET.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256
        ).hexdigest()

    def get_timestamp(self):
        return int(time.time() * 1000)

    def dispatch_request(self, http_method):
        session = requests.Session()
        session.headers.update(
            {"Content-Type": "application/json;charset=utf-8", "X-MBX-APIKEY": self.KEY}
        )
        return {
            "GET": session.get,
            "DELETE": session.delete,
            "PUT": session.put,
            "POST": session.post,
        }.get(http_method, "GET")

    def send_signed_request(self, http_method, url_path, payload={}):
        query_string = urlencode(payload)
        # replace single quote to double quote
        query_string = query_string.replace("%27", "%22")
        if query_string:
            query_string = "{}&timestamp={}".format(query_string, self.get_timestamp())
        else:
            query_string = "timestamp={}".format(self.get_timestamp())

        url = (
            self.BASE_URL + url_path + "?" + query_string + "&signature=" + self.hashing(query_string)
        )
        print("{} {}".format(http_method, url))
        params = {"url": url, "params": {}}
        response = self.dispatch_request(http_method)(**params)
        return response.json()

    def send_public_request(self, url_path, payload={}):
        query_string = urlencode(payload, True)
        url = self.BASE_URL + url_path
        if query_string:
            url = url + "?" + query_string
        print("{}".format(url))
        response = self.dispatch_request("GET")(url=url)
        return response.json()
    
class SpotAPIHandler:
    def __init__(self, base_url='https://testnet.binance.vision', api_key=None, secret_key=None):
        self.BASE_URL = base_url
        self.API_KEY = api_key
        self.SECRET_KEY = secret_key

    def query_binance_status(self):
        status = Spot(base_url=self.BASE_URL).system_status()
        if status["status"] == 0:
            print(True)
            return True
        else:
            raise ConnectionError

    def query_account(self):
        return Spot(
            api_key=self.API_KEY,
            api_secret=self.SECRET_KEY,
            base_url=self.BASE_URL,
        ).account()

    def query_testnet(self):
        client = Spot(base_url=self.BASE_URL)
        print(client.time())

    def get_candlestick_data(self, symbol, timeframe, qty):
        raw_data = Spot(base_url=self.BASE_URL).klines(symbol=symbol, interval=timeframe, limit=qty)
        converted_data = []
        for candle in raw_data:
            converted_candle = {
                "time": candle[0],
                "open": float(candle[1]),
                "high": float(candle[2]),
                "low": float(candle[3]),
                "close": float(candle[4]),
                "volume": float(candle[5]),
                "close_time": candle[6],
                "quote_asset_volume": float(candle[7]),
                "number_of_trades": int(candle[8]),
                "taker_buy_base_asset_volume": float(candle[9]),
                "taker_buy_quote_asset_volume": float(candle[10]),
            }
            converted_data.append(converted_candle)
        return converted_data

    def query_quote_asset_list(self, quote_asset_symbol):
        symbol_dictionary = Spot(base_url=self.BASE_URL).exchange_info()
        # convert this into dataframe
        symbol_dataframe = pandas.DataFrame(symbol_dictionary["symbols"])
        # Extract all the symbols with the base asset pair (ETH)
        quote_symbol_dataframe = symbol_dataframe.loc[
            symbol_dataframe["quoteAsset"] == quote_asset_symbol
        ]
        quote_symbol_dataframe = quote_symbol_dataframe.loc[
            quote_symbol_dataframe["status"] == "TRADING"
        ]
        return quote_symbol_dataframe

    def make_trade_with_params(self, paramas, project_settings):
        print("Making trade with params")
        # Set API key
        api_key = project_settings["BinanceKeys"]["API_KEY"]
        secret_key = project_settings["BinanceKeys"]["SECRET_KEY"]
        # Create client
        client = Spot(
            api_key=api_key,
            api_secret=secret_key,
            base_url=self.BASE_URL,
        )

        # Make the trade
        try:
            response = client.new_order(**paramas)
            return response
        except ConnectionRefusedError as error:
            print(f"Error: {error}")

    def query_open_trades(self, project_settings):
        # Set the API Key
        api_key = project_settings["BinanceKeys"]["API_Key"]
        # Set the secret key
        secret_key = project_settings["BinanceKeys"]["Secret_Key"]
        # Setup the client
        client = Spot(
            api_key=api_key,
            api_secret=secret_key,
            base_url=self.BASE_URL,
        )

        # get Trades
        try:
            response = client.get_open_orders()
            return response
        except ConnectionRefusedError as error:
            print(f"Error: {error}")

    def cancel_order_by_symbol(self, symbol, project_settings):
        # Set the API Key
        api_key = project_settings["BinanceKeys"]["API_Key"]
        # Set the secret key
        secret_key = project_settings["BinanceKeys"]["Secret_Key"]
        # Setup the client
        client = Spot(
            api_key=api_key,
            api_secret=secret_key,
            base_url=self.BASE_URL,
        )

        # Cancel the trade
        try:
            response = client.cancel_open_orders(symbol=symbol)
            return response
        except ConnectionRefusedError as error:
            print(f"Found error {error}")

    def place_limit_order(self, symbol, side, quantity, price, project_settings):
        # Set the API Key
        api_key = project_settings["BinanceKeys"]["API_Key"]
        # Set the secret key
        secret_key = project_settings["BinanceKeys"]["Secret_Key"]
        # Setup the client
        client = Spot(
            key=api_key, secret=secret_key, base_url=self.BASE_URL
        )

        # Place the limit order
        try:
            response = client.new_order(
                symbol=symbol,
                side=side,
                type="LIMIT",
                timeInForce="GTC",
                quantity=quantity,
                price=price,
            )
            return response
        except ConnectionRefusedError as error:
            print(f"Found error {error}")

    def place_stop_loss_order(
        self, symbol, side, quantity, stop_price, limit_price, project_settings
    ):
        # Set the API Key
        api_key = project_settings["BinanceKeys"]["API_Key"]
        # Set the secret key
        secret_key = project_settings["BinanceKeys"]["Secret_Key"]
        # Setup the client
        client = Spot(
            key=api_key, secret=secret_key, base_url=self.BASE_URL
        )

        # Place the stop loss order
        try:
            response = client.new_order(
                symbol=symbol,
                side=side,
                type="STOP_LOSS_LIMIT",
                timeInForce="GTC",
                quantity=quantity,
                stopPrice=stop_price,
                price=limit_price,
            )
            return response
        except ConnectionRefusedError as error:
            print(f"Found error {error}")

    def place_take_profit_order(
        self, symbol, side, quantity, stop_price, limit_price, project_settings
    ):
        # Set the API Key
        api_key = project_settings["BinanceKeys"]["API_Key"]
        # Set the secret key
        secret_key = project_settings["BinanceKeys"]["Secret_Key"]
        # Setup the client
        client = Spot(
            key=api_key, secret=secret_key, base_url=self.BASE_URL
        )

        # Place the take profit order
        try:
            response = client.new_order(
                symbol=symbol,
                side=side,
                type="TAKE_PROFIT_LIMIT",
                timeInForce="GTC",
                quantity=quantity,
                stopPrice=stop_price,
                price=limit_price,
            )
            return response
        except ConnectionRefusedError as error:
            print(f"Found error {error}")

if __name__ == "__main__":
    # Test Spot
    print("spot...")
    spot_api_key, spot_api_secret = get_api_key("spot")
    handler = SpotAPIHandler(api_key=spot_api_key, secret_key=spot_api_secret)
    account = handler.query_account()
    print(account['balances'][1])
    print(account['balances'][4])

    # Test Future
    print("future...")
    future_api_key, future_api_secret = get_api_key("future")
    BASE_URL = "https://testnet.binancefuture.com"  # testnet base url
    handler = FutureAPIHandler(BASE_URL, future_api_key, future_api_secret)
    f_account = handler.send_signed_request("GET", "/fapi/v2/account")
    print(f_account['assets'][1])
    print(f_account['assets'][4])

    premiumIndex = handler.send_signed_request("GET", "/fapi/v1/premiumIndex",{"symbol": "BTCUSDT"})
    print("lastFundingRate", premiumIndex["lastFundingRate"])
    print("indexPrice", premiumIndex["indexPrice"])
    current_price  = round(float(premiumIndex["indexPrice"]), 0)