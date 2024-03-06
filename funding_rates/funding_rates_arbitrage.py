import ccxt
import pandas as pd
import datetime
from dataFetcher import DataFetcher
import matplotlib.pyplot as plt
import datetime
import matplotlib.dates as mdates


if __name__ == '__main__':
    exchange_instance = ccxt.binance()
    data_fetcher = DataFetcher(exchange_instance)

    coins = ['BTC', 'ETH', 'XRP', 'ADA', 'DOT', 'LINK', 'LTC', 'BCH', 'XLM', 'UNI']
    start_date = '2022-01-01'
    end_date = '2023-01-01'
    results = {}

    for coin in coins:
        spot_symbol = f"{coin}/USDT"
        contract_symbol = f"{coin}/USDT:USDT"
        results[coin] = data_fetcher.fetch_and_merge_data(spot_symbol, contract_symbol, start_date, end_date)
    
    # print(results.keys())
    # print(results['BTC'])

    checkout = 'BTC'
    # 轉換timestamp為可讀的日期
    results[checkout].index = pd.to_datetime(results[checkout].index, unit='ms')

    # 繪製資金費率
    plt.figure(figsize=(16, 6))
    plt.plot(results[checkout].index, results[checkout]['fundingRate'], label='Funding Rate', color='blue')
    plt.fill_between(results[checkout].index, results[checkout]['fundingRate'], color='blue', alpha=0.2)
    plt.title(f'{checkout} Funding Rate Over Time')  # 使用f-string格式化
    plt.xlabel('Date')
    plt.ylabel('Funding Rate*1000')
    plt.grid(True)
    plt.tight_layout()
    plt.legend()
    plt.show()