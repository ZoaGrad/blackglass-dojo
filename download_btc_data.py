import yfinance as yf
import pandas as pd
import os

def download_2022_data():
    print("Downloading BTC-USD daily data for 2022...")
    # Fetch BTC-USD data for 2022
    data = yf.download("BTC-USD", start="2022-01-01", end="2023-01-01", interval="1d")
    
    if data.empty:
        print("Error: No data downloaded.")
        return
    
    # Flatten multi-index columns if they exist (yfinance 0.2.x behavior)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    
    # Save to CSV
    os.makedirs("data", exist_ok=True)
    file_path = "data/btc_usd_2022.csv"
    data.to_csv(file_path)
    print(f"Data saved to {file_path}")
    print(data.head())

if __name__ == "__main__":
    download_2022_data()
