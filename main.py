import streamlit as st
from heikin_ashi import compute_heikin_ashi, detect_doji
from upstox_utils import fetch_ohlc, place_order
from backtest import backtest_strategy
import pandas as pd

st.set_page_config(page_title="Heikin Ashi Doji Trader", layout="wide")
st.title("Heikin Ashi Doji Trader (Upstox)")

with st.sidebar:
    st.header("Upstox API Credentials")
    api_key = st.text_input("Upstox API Key", type="password")
    api_secret = st.text_input("Upstox API Secret", type="password")
    access_token = st.text_input("Upstox Access Token", type="password")
    st.markdown("Don't share your credentials. Use test/demo accounts for development.")

symbol = st.text_input("Instrument Token (e.g. NSE_EQ|RELIANCE)", value="NSE_EQ|RELIANCE")
interval = st.selectbox("Timeframe", ["15minute", "5minute", "day"])
days = st.slider("Days of Data", 1, 30, 5)

col1, col2 = st.columns(2)

with col1:
    if st.button("Fetch & Analyze Data"):
        if not access_token or not symbol:
            st.error("Please provide Access Token and Instrument Token.")
        else:
            df = fetch_ohlc(symbol, interval, days, access_token)
            if df is None or df.empty:
                st.error("No data fetched. Check symbol or credentials.")
            else:
                ha_df = compute_heikin_ashi(df)
                ha_df = detect_doji(ha_df)
                st.write("Recent Heikin Ashi Candles", ha_df.tail(10))
                st.line_chart(ha_df.set_index("datetime")[["HA_Open", "HA_Close"]])
                last_doji = ha_df.iloc[-1]['Doji']
                if last_doji:
                    st.success("Doji Detected on Last Candle!")
                    if st.button("Place Live Order"):
                        order_result = place_order(symbol, access_token)
                        st.write("Order Response:", order_result)
                else:
                    st.info("No Doji detected on the last candle.")

with col2:
    st.header("Backtesting")
    if st.button("Run Backtest"):
        if not access_token or not symbol:
            st.error("Please provide Access Token and Instrument Token.")
        else:
            df = fetch_ohlc(symbol, interval, days, access_token)
            if df is None or df.empty:
                st.error("No data fetched. Check symbol or credentials.")
            else:
                ha_df = compute_heikin_ashi(df)
                ha_df = detect_doji(ha_df)
                result = backtest_strategy(ha_df)
                st.subheader("Backtest Result")
                st.write(f"Final Cash: ₹{result['final_cash']:.2f}")
                st.write("Trades Executed:")
                for t in result['trades']:
                    st.write(t)