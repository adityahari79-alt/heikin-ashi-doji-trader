import requests
import pandas as pd
from datetime import datetime, timedelta

def fetch_ohlc(token, interval, days, access_token):
    try:
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        url = f"https://api.upstox.com/v2/historical-candle/{token}/{interval}"
        headers = {'Authorization': f'Bearer {access_token}'}
        params = {
            'from': start_time.strftime('%Y-%m-%d'),
            'to': end_time.strftime('%Y-%m-%d')
        }
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code != 200:
            return pd.DataFrame()
        data = response.json()
        if 'data' not in data or 'candles' not in data['data']:
            return pd.DataFrame()
        candles = data['data']['candles']
        df = pd.DataFrame(candles, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
        df['datetime'] = pd.to_datetime(df['datetime'])
        df[['open', 'high', 'low', 'close']] = df[['open', 'high', 'low', 'close']].astype(float)
        return df
    except Exception as e:
        return pd.DataFrame()

def place_order(token, access_token):
    # This is a placeholder for actual Upstox order placement.
    # Replace this with real API call as per Upstox documentation.
    # For safety, demo returns a simulated response.
    # To place a real order, use the Upstox API order endpoint with your parameters.
    # Example: buy 1 share at market price.
    # See: https://upstox.com/developer/api/
    return {"status": "Order simulated. (Implement real order logic as needed.)"}