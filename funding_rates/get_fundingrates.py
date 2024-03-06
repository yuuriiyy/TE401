import ccxt
import datetime

# Initialize the Binance exchange object
exchange = ccxt.binance()

# Define the symbol for the contract you are interested in
symbol = 'BTCUSDT'

# Fetch the current funding rate
funding_info = exchange.fetch_premium_index(symbol)
funding_rate = funding_info['lastFundingRate']
next_funding_time = datetime.datetime.utcfromtimestamp(funding_info['nextFundingTime'] / 1000)

print(f"Funding Rate for {symbol}: {funding_rate}")
print(f"Next Funding Time: {next_funding_time}")