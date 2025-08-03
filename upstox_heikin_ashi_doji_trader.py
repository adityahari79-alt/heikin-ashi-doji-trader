import requests
import websocket
import threading
import time
import json
from datetime import datetime, timedelta

class UpstoxLiveHeikinAshiDojiTrader:
    def __init__(self, api_key, api_secret, redirect_uri, instrument_token, on_doji_detected=None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.redirect_uri = redirect_uri
        self.instrument_token = instrument_token
        self.access_token = None
        self.refresh_token = None
        self.ws = None
        self.candles = {}  # minute -> ohlc
        self.heikin_ashi_candles = []
        self.on_doji_detected = on_doji_detected

    def authenticate(self):
        print("Visit this URL and authorize the app, then paste the 'code' parameter from the callback URL:")
        auth_url = (
            f"https://api.upstox.com/v2/login/authorization/dialog"
            f"?response_type=code"
            f"&client_id={self.api_key}"
            f"&redirect_uri={self.redirect_uri}"
        )
        print(auth_url)
        code = input("Enter the 'code' from the redirected URL: ").strip()

        # Exchange code for access token
        token_url = "https://api.upstox.com/v2/login/authorization/token"
        payload = {
            "client_id": self.api_key,
            "client_secret": self.api_secret,
            "code": code,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code"
        }
        resp = requests.post(token_url, data=payload)
        data = resp.json()
        if "access_token" in data:
            self.access_token = data["access_token"]
            self.refresh_token = data.get("refresh_token")
            print("Authentication successful.")
        else:
            raise Exception(f"Failed to authenticate: {data}")

    def start_websocket(self):
        ws_url = f"wss://api.upstox.com/v2/feed/market-data-feed/socket/websocket?access_token={self.access_token}"
        self.ws = websocket.WebSocketApp(
            ws_url,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        wst = threading.Thread(target=self.ws.run_forever)
        wst.daemon = True
        wst.start()
        print("WebSocket started.")
        # Keep thread alive
        while True:
            time.sleep(1)

    def on_open(self, ws):
        msg = {
            "guid": "doji-trader-1",
            "method": "sub",
            "data": {"instrumentKeys": [self.instrument_token]}
        }
        ws.send(json.dumps(msg))
        print(f"Subscribed to {self.instrument_token}")

    def on_message(self, ws, message):
        try:
            data = json.loads(message)
            if "data" not in data:
                return
            tick = data["data"]
            instrument = tick["instrument_token"] if "instrument_token" in tick else self.instrument_token
            price = float(tick.get("last_price", 0))
            volume = int(tick.get("volume_traded_today", 0))
            # Convert exchange_time (ms) to datetime
            ts = int(tick.get("exchange_time", 0))
            if ts > 1e12:  # Upstox gives ms, convert to sec
                ts = ts // 1000
            timestamp = datetime.fromtimestamp(ts)
            minute = timestamp.replace(second=0, microsecond=0)

            prev_candle = self.candles.get(minute)
            if not prev_candle:
                candle = {
                    "open": price,
                    "high": price,
                    "low": price,
                    "close": price,
                    "volume": volume
                }
            else:
                candle = prev_candle
                candle["high"] = max(candle["high"], price)
                candle["low"] = min(candle["low"], price)
                candle["close"] = price
                candle["volume"] = volume  # Upstox gives cumulative volume

            self.candles[minute] = candle

            # Check if previous minute candle is complete
            prev_minute = minute - timedelta(minutes=1)
            if prev_minute in self.candles:
                prev_ohlc = self.candles.pop(prev_minute)
                ha_candle = self.calculate_heikin_ashi(prev_ohlc)
                self.heikin_ashi_candles.append(ha_candle)
                if self.is_doji(ha_candle):
                    print(f"Doji detected at {prev_minute}! {ha_candle}")
                    if self.on_doji_detected:
                        self.on_doji_detected(prev_minute, ha_candle)
        except Exception as e:
            print(f"Error in on_message: {e}")

    def calculate_heikin_ashi(self, ohlc):
        if not self.heikin_ashi_candles:
            ha_open = (ohlc["open"] + ohlc["close"]) / 2
            ha_close = (ohlc["open"] + ohlc["high"] + ohlc["low"] + ohlc["close"]) / 4
        else:
            prev_ha = self.heikin_ashi_candles[-1]
            ha_open = (prev_ha["open"] + prev_ha["close"]) / 2
            ha_close = (ohlc["open"] + ohlc["high"] + ohlc["low"] + ohlc["close"]) / 4
        ha_high = max(ohlc["high"], ha_open, ha_close)
        ha_low = min(ohlc["low"], ha_open, ha_close)
        return {
            "open": ha_open,
            "high": ha_high,
            "low": ha_low,
            "close": ha_close,
            "volume": ohlc["volume"]
        }

    def is_doji(self, ha):
        # Simple Doji: body very small compared to range
        body = abs(ha["open"] - ha["close"])
        rng = ha["high"] - ha["low"]
        return rng > 0 and body / rng < 0.1

    def on_error(self, ws, error):
        print("WebSocket error:", error)

    def on_close(self, ws, *args):
        print("WebSocket closed.")

    def run(self):
        self.authenticate()
        self.start_websocket()

# =================
# Example usage:
# =================

if __name__ == "__main__":
    # Fill with your Upstox credentials and instrument token
    API_KEY = "YOUR_API_KEY"
    API_SECRET = "YOUR_API_SECRET"
    REDIRECT_URI = "YOUR_REDIRECT_URI"
    INSTRUMENT_TOKEN = "NSE_INDEX|Nifty 50"  # Example

    def handle_doji(minute, ha_candle):
        print(f"Callback: Doji detected at {minute}: {ha_candle}")

    trader = UpstoxLiveHeikinAshiDojiTrader(
        api_key=API_KEY,
        api_secret=API_SECRET,
        redirect_uri=REDIRECT_URI,
        instrument_token=INSTRUMENT_TOKEN,
        on_doji_detected=handle_doji
    )
    trader.run()