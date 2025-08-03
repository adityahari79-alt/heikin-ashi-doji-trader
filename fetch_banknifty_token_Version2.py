import requests
import pandas as pd

def get_instrument_token(access_token, symbol_name="Nifty Bank", exchange="NSE_INDEX"):
    """
    Fetch the instrument token for a given symbol name (e.g., 'Nifty Bank') from Upstox.
    :param access_token: Your Upstox API access token (string)
    :param symbol_name: The display name of the instrument (default: 'Nifty Bank')
    :param exchange: The exchange segment (default: 'NSE_INDEX')
    :return: The instrument token as a string, or None if not found
    """
    # You can also download the CSV from https://assets.upstox.com/market-quote/instruments/exchange/complete.csv
    url = "https://api.upstox.com/v2/market-quote/instruments"
    headers = {"Authorization": f"Bearer {access_token}"}
    resp = requests.get(url, headers=headers, timeout=30)
    if resp.status_code != 200:
        print("Failed to fetch instruments. Status:", resp.status_code)
        print(resp.text)
        return None

    # The response is a CSV string, so parse with pandas
    # If the API returns JSON, adapt accordingly
    try:
        # Try CSV (as per current Upstox docs)
        from io import StringIO
        df = pd.read_csv(StringIO(resp.text))
    except Exception:
        # If JSON, parse as JSON
        try:
            data = resp.json()
            if "data" in data:
                df = pd.DataFrame(data["data"])
            else:
                print("No instrument data found in JSON.")
                return None
        except Exception as e:
            print("Failed to parse instrument data:", e)
            return None

    # Search for the symbol
    filtered = df[
        (df['exchange'] == exchange) &
        (df['symbol'].str.strip().str.lower() == symbol_name.strip().lower())
    ]
    if filtered.empty:
        print(f"Could not find instrument token for {exchange}|{symbol_name}")
        return None

    token = filtered.iloc[0]['instrument_token']
    print(f"Instrument token for {exchange}|{symbol_name}: {token}")
    return token

if __name__ == "__main__":
    # Replace with your valid Upstox API access token
    ACCESS_TOKEN = "YOUR_ACCESS_TOKEN"
    token = get_instrument_token(ACCESS_TOKEN, symbol_name="Nifty Bank", exchange="NSE_INDEX")
    print("Bank Nifty instrument token:", token)