import yfinance as yf

def update_dataset():
    print("Fetching latest Bitcoin data from 2020 to today...")
    data = yf.download("BTC-USD", start="2020-01-01")
    data.to_csv("bitcoin_prices.csv")
    print("Successfully updated bitcoin_prices.csv!")

if __name__ == "__main__":
    update_dataset()
