# Heikin Ashi Doji Trading System (Upstox)

An interactive trading and backtesting tool for Heikin Ashi Doji strategies on Upstox.

## Features

- **Streamlit GUI**: Easy-to-use interface.
- **Backtesting**: Simulate strategy performance.
- **Live Data**: Fetches recent OHLC data using Upstox API.
- **Order Placement**: (Demo/simulated) Place live trades when Doji detected.

## Requirements

- Python 3.8+
- Upstox API credentials (use test/demo account for development)

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
streamlit run main.py
```

- Enter your Upstox API credentials in the sidebar.
- Set instrument token (e.g., `NSE_EQ|RELIANCE`), timeframe, and number of days.
- Fetch and analyze data, run backtests, or place orders.

## Notes

- **Order placement is simulated by default.**  
  To place real orders, implement the logic in `upstox_utils.py` as per Upstox API documentation.
- **Always test with demo accounts first.**  
  Use proper error-handling and logging for production use.

## File Structure

```
main.py              # Streamlit GUI
heikin_ashi.py       # Heikin Ashi and Doji logic
upstox_utils.py      # Upstox API integration
backtest.py          # Backtesting logic
requirements.txt     # Dependencies
README.md            # Documentation
```