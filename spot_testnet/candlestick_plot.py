import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd

# Your candlestick data
def plotCandles(candles_data, symbol):
    # Convert data to pandas DataFrame
    df = pd.DataFrame(candles_data)
    df['time'] = pd.to_datetime(df['time'], unit='ms')
    df.set_index('time', inplace=True)

    # Plotting the candlestick chart
    mpf.plot(df, type='candle', style='yahoo', volume=True, title=f'{symbol} Candlestick Chart', ylabel=f'Price ({symbol})')

    plt.show()
