import ccxt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import matplotlib.dates as mdates
import sqlite3

# Function to calculate the moving average
def calculate_moving_average(data, window_size):
    return data.rolling(window=window_size).mean()

# Function to create or connect to an SQLite database
def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"Connected to {db_file}")
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn

# Function to create a new table for a coin's funding rate
def create_table(conn, coin):
    try:
        cursor = conn.cursor()
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {coin}_funding_rate (
                timestamp INTEGER PRIMARY KEY,
                close_contract REAL,
                close_spot REAL,
                funding_rate REAL,
                signal BOOLEAN
            );
        ''')
        conn.commit()
        print(f"Table {coin}_funding_rate created successfully")
    except sqlite3.Error as e:
        print(e)

# Function to insert data into the table
def insert_data(conn, coin, data):
    try:
        cursor = conn.cursor()
        cursor.executemany(f'''
            INSERT INTO {coin}_funding_rate (timestamp, close_contract, close_spot, funding_rate, signal)
            VALUES (?, ?, ?, ?, ?)
        ''', data)
        conn.commit()
        print("Data inserted successfully")
    except sqlite3.Error as e:
        print(e)

# Remaining code remains unchanged
# 使用一個函數獲取所有數據
def fetch_all_data(symbol, timeframe, since, end):
    all_data = []
    while since < end:
        data = exchange.fetch_ohlcv(symbol, timeframe, since=since, limit=1000)
        if len(data) == 0:  # 如果沒有新的數據，則跳出循環
            break
        since = data[-1][0] + 1  # 更新時間戳以獲取下一批數據
        all_data.extend(data)
    return all_data

def fetch_and_merge_data(spot_symbol, contract_symbol, exchange, start_date, end_date):
    all_funding_rates = []
    since_timestamp = int(datetime.datetime.strptime(start_date, '%Y-%m-%d').timestamp() * 1000)
    end_timestamp = int(datetime.datetime.strptime(end_date, '%Y-%m-%d').timestamp() * 1000)
    last_timestamp = since_timestamp

    # Fetch Spot Price Data
    spot_ohlcv_8h = fetch_all_data(spot_symbol, '8h', since_timestamp, end_timestamp)
    spot_df_8h = pd.DataFrame(spot_ohlcv_8h, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    spot_df_8h['date'] = pd.to_datetime(spot_df_8h['timestamp'], unit='ms')
    # Filter the dataframes based on date
    spot_df_8h = spot_df_8h[(spot_df_8h['date'] >= pd.Timestamp(start_date)) & (spot_df_8h['date'] < pd.Timestamp(end_date))]
    spot_df_8h.set_index('date', inplace=True)

    # Fetch Perpetual Contract Price Data
    ohlcv_8h = fetch_all_data(contract_symbol, '8h', since_timestamp, end_timestamp)
    df_8h = pd.DataFrame(ohlcv_8h, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df_8h['date'] = pd.to_datetime(df_8h['timestamp'], unit='ms')
    df_8h = df_8h[(df_8h['date'] >= pd.Timestamp(start_date)) & (df_8h['date'] < pd.Timestamp(end_date))]

    # Fetch Funding Rates
    while last_timestamp < end_timestamp:
        funding_rates = exchange.fetchFundingRateHistory(contract_symbol, since=last_timestamp, params={"endTime": end_timestamp})
        if not funding_rates:
            break
        all_funding_rates.extend(funding_rates)
        last_timestamp = funding_rates[-1]['timestamp'] + 1

    funding_df = pd.DataFrame(all_funding_rates)
    funding_df['date'] = pd.to_datetime(funding_df['timestamp'], unit='ms')
    funding_df['adjusted_timestamp'] = (funding_df['timestamp'] // (8 * 60 * 60 * 1000)) * (8 * 60 * 60 * 1000)
    funding_df['adjusted_date'] = pd.to_datetime(funding_df['adjusted_timestamp'], unit='ms')
    funding_df.set_index('adjusted_date', inplace=True)

    # Merge Data
    merged_df = df_8h.merge(spot_df_8h[['close']], on='date', how='left', suffixes=('', '_spot'))
    merged_df = merged_df.merge(funding_df[['fundingRate']], left_on='date', right_on='adjusted_date', how='left')
    merged_df.set_index('timestamp', inplace=True)
    merged_df.rename(columns={'close': 'close_contract'}, inplace=True)
    
    return merged_df[['close_contract', 'close_spot', 'fundingRate']]

db_connection = create_connection("funding_rate_database.db")
# Define coins and their contract counterparts
coins = ['BTC'] #, 'ETH', 'XRP', 'ADA', 'DOT', 'LINK', 'LTC', 'BCH', 'XLM', 'UNI']
exchange = ccxt.binance()
start_date = '2024-03-01'
end_date = '2024-03-21'

results = {}
for coin in coins:
    spot_symbol = f"{coin}/USDT"
    contract_symbol = f"{coin}/USDT:USDT"
    results[coin] = fetch_and_merge_data(spot_symbol, contract_symbol, exchange, start_date, end_date)
    print(results[coin])
    # Convert timestamp to readable date
    results[coin].index = pd.to_datetime(results[coin].index, unit='ms')

    # Create the table if it doesn't exist
    create_table(db_connection, coin)

    # Convert the DataFrame to a list of tuples for easier insertion
    data_to_insert = [
        (timestamp, close_contract, close_spot, funding_rate)
        for timestamp, close_contract, close_spot, funding_rate in zip(
            results[coin].index.astype(int) // 10**6,
            results[coin]['close_contract'],
            results[coin]['close_spot'],
            results[coin]['fundingRate'],
        )
    ]

    # Insert data into the table
    insert_data(db_connection, coin, data_to_insert)




# Close the database connection
# db_connection.close()

# Calculate 10-day moving average of funding rate
results[coin]['fundingRate_10MA'] = calculate_moving_average(results[coin]['fundingRate'], 10)

# Create signal column based on comparison of funding rate and its 10-day moving average
results[coin]['signal'] = results[coin]['fundingRate'] > results[coin]['fundingRate_10MA']

# Convert True/False to 1/0 for storage in SQLite
results[coin]['signal'] = results[coin]['signal'].astype(int)

# Convert the DataFrame to a list of tuples for easier insertion
data_to_insert = [
    (timestamp, close_contract, close_spot, funding_rate, signal)
    for timestamp, close_contract, close_spot, funding_rate, signal in zip(
        results[coin].index.astype(int) // 10**6,
        results[coin]['close_contract'],
        results[coin]['close_spot'],
        results[coin]['fundingRate'],
        results[coin]['signal']
    )
]

# Insert data into the table
insert_data(db_connection, coin, data_to_insert)

# Close the database connection
db_connection.close()
