import pandas as pd

def compute_heikin_ashi(df):
    ha_df = df.copy()
    ha_df['HA_Close'] = (df['open'] + df['high'] + df['low'] + df['close']) / 4
    ha_open = [(df['open'].iloc[0] + df['close'].iloc[0]) / 2]
    for i in range(1, len(df)):
        ha_open.append((ha_open[i-1] + ha_df['HA_Close'].iloc[i-1]) / 2)
    ha_df['HA_Open'] = ha_open
    ha_df['HA_High'] = ha_df[['HA_Open', 'HA_Close', 'high']].max(axis=1)
    ha_df['HA_Low'] = ha_df[['HA_Open', 'HA_Close', 'low']].min(axis=1)
    return ha_df

def detect_doji(ha_df, threshold=0.1):
    def is_doji(row):
        body = abs(row['HA_Close'] - row['HA_Open'])
        candle_range = row['HA_High'] - row['HA_Low']
        return body <= threshold * candle_range if candle_range != 0 else False
    ha_df['Doji'] = ha_df.apply(is_doji, axis=1)
    return ha_df