def backtest_strategy(ha_df):
    # Simple backtest: Buy on Doji, Sell on next non-Doji
    cash = 100000
    position = 0
    buy_price = 0
    trades = []
    for idx, row in ha_df.iterrows():
        if position == 0 and row['Doji']:
            position = 1
            buy_price = row['HA_Close']
            trades.append(f"Buy at {buy_price:.2f} ({row['datetime']})")
        elif position == 1 and not row['Doji']:
            sell_price = row['HA_Close']
            profit = sell_price - buy_price
            cash += profit
            trades.append(f"Sell at {sell_price:.2f} ({row['datetime']}) Profit: {profit:.2f}")
            position = 0
    # If holding position at end, sell at last close
    if position == 1:
        sell_price = ha_df.iloc[-1]['HA_Close']
        profit = sell_price - buy_price
        cash += profit
        trades.append(f"Sell at {sell_price:.2f} (End) Profit: {profit:.2f}")
    return {"final_cash": cash, "trades": trades}