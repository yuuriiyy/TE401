import json

def 
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

# PERCENT_PRICE_BY_SIDE
def check_percent_price_by_side():
    """The PERCENT_PRICE_BY_SIDE filter defines the valid range for the price based on the average of the previous trades.

    avgPriceMins is the number of minutes the average price is calculated over. 0 means the last price is used.
    There is a different range depending on whether the order is placed on the BUY side or the SELL side.

    Buy orders will succeed on this filter if:

    - Order price <= weightedAveragePrice * bidMultiplierUp
    - Order price >= weightedAveragePrice * bidMultiplierDown
    
    Sell orders will succeed on this filter if:

    - Order Price <= weightedAveragePrice * askMultiplierUp
    - Order Price >= weightedAveragePrice * askMultiplierDown
    """
    
    
# PERCENT_PRICE
def 