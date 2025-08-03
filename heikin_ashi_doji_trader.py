import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
# from upstox_api.api import Upstox  # Uncomment if using official SDK

# ----------- CONFIGURATION -----------
UPSTOX_API_KEY = 'YOUR_API_KEY'
UPSTOX_API_SECRET = 'YOUR_API_SECRET'
UPSTOX_ACCESS_TOKEN = 'YOUR_ACCESS_TOKEN'
INSTRUMENT_TOKEN = 'NSE_EQ|RELIANCE'   # Example: NSE_EQ|RELIANCE

# ----------- UTILITY FUNCTIONS -----------
def fetch_historical_data(token, interval='15minute', days=5):
    """
    Fetch historical OHLC data using Upstox API.
    Returns a DataFrame with columns: datetime, open, high, low, close
    """
    end_time = datetime.now()
    start_time = end_time - timedelta(days=days)
    url = f"https://api.upstox.com/v2/historical-candle/{token}/{interval}"
    headers = {'Authorization': f'Bearer {UPSTOX_ACCESS_TOKEN}'}
    params = {
        'from': start_time.strftime('%Y-%m-%d'),
        'to': end_time.strftime('%Y-%m-%d')
    }
    response = requests.get(url, headers=headers, params=params)
    data = response.json()['data']['candles']
    df = pd.DataFrame(data, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
    df['datetime'] = pd.to_datetime(df['datetime'])
    df[['open', 'high', 'low', 'close']] = df[['open', 'high', 'low', 'close']].astype(float)
    return df

def heikin_ashi(df):
    """
    Compute Heikin Ashi candles and add to DataFrame.
    """
    ha_df = df.copy()
    ha_df['HA_Close'] = (df['open'] + df['high'] + df['low'] + df['close']) / 4
    ha_open = [(df['open'][0] + df['close'][0]) / 2]
    for i in range(1, len(df)):
        ha_open.append((ha_open[i-1] + ha_df['HA_Close'][i-1]) / 2)
    ha_df['HA_Open'] = ha_open
    ha_df['HA_High'] = ha_df[['HA_Open', 'HA_Close', 'high']].max(axis=1)
    ha_df['HA_Low'] = ha_df[['HA_Open', 'HA_Close', 'low']].min(axis=1)
    return ha_df

def is_doji(row, threshold=0.1):
    """
    Identifies a Heikin Ashi Doji candle.
    """
    body = abs(row['HA_Close'] - row['HA_Open'])
    candle_range = row['HA_High'] - row['HA_Low']
    return body <= threshold * candle_range

def detect_doji(ha_df, threshold=0.1):
    """
    Adds a column indicating if the Heikin Ashi candle is a Doji.
    """
    ha_df['Doji'] = ha_df.apply(is_doji, axis=1, threshold=threshold)
    return ha_df

# ----------- MAIN LOGIC -----------
def main():
    df = fetch_historical_data(INSTRUMENT_TOKEN, interval='15minute', days=5)
    ha_df = heikin_ashi(df)
    ha_df = detect_doji(ha_df)

    # Print detected Dojis
    dojis = ha_df[ha_df['Doji']]
    print("Detected Heikin Ashi Doji candles:")
    print(dojis[['datetime', 'HA_Open', 'HA_High', 'HA_Low', 'HA_Close']])

    # --- Example: Place a trade if last candle is Doji
    if ha_df.iloc[-1]['Doji']:
        print("Heikin Ashi Doji detected on last candle! Place your trade logic here.")
        # Place order using Upstox API (Uncomment and implement as needed)
        # u = Upstox(UPSTOX_API_KEY, UPSTOX_API_SECRET)
        # u.set_access_token(UPSTOX_ACCESS_TOKEN)
        # u.place_order(...)

if __name__ == "__main__":
    main()