import ccxt
import pandas as pd
import datetime

class DataFetcher:
    def __init__(self, exchange):
        self.exchange = exchange

    def fetch_all_data(self, symbol, timeframe, since, end):
        all_data = []
        while since < end:
            data = self.exchange.fetch_ohlcv(symbol, timeframe, since=since, limit=1000)
            if len(data) == 0:
                break
            since = data[-1][0] + 1
            all_data.extend(data)
        return all_data

    def fetch_and_merge_data(self, spot_symbol, contract_symbol, start_date, end_date):
        all_funding_rates = []
        since_timestamp = int(datetime.datetime.strptime(start_date, '%Y-%m-%d').timestamp() * 1000)
        end_timestamp = int(datetime.datetime.strptime(end_date, '%Y-%m-%d').timestamp() * 1000)
        last_timestamp = since_timestamp

        # Fetch Spot Price Data
        spot_ohlcv_8h = self.fetch_all_data(spot_symbol, '8h', since_timestamp, end_timestamp)
        spot_df_8h = pd.DataFrame(spot_ohlcv_8h, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        spot_df_8h['date'] = pd.to_datetime(spot_df_8h['timestamp'], unit='ms')
        spot_df_8h = spot_df_8h[(spot_df_8h['date'] >= pd.Timestamp(start_date)) & (spot_df_8h['date'] < pd.Timestamp(end_date))]
        spot_df_8h.set_index('date', inplace=True)

        # Fetch Perpetual Contract Price Data
        ohlcv_8h = self.fetch_all_data(contract_symbol, '8h', since_timestamp, end_timestamp)
        df_8h = pd.DataFrame(ohlcv_8h, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df_8h['date'] = pd.to_datetime(df_8h['timestamp'], unit='ms')
        df_8h = df_8h[(df_8h['date'] >= pd.Timestamp(start_date)) & (df_8h['date'] < pd.Timestamp(end_date))]

        # Fetch Funding Rates
        while last_timestamp < end_timestamp:
            funding_rates = self.exchange.fetchFundingRateHistory(contract_symbol, since=last_timestamp, params={"endTime": end_timestamp})
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