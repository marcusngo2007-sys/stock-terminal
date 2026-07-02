import yfinance as yf

def get_price_history(ticker: str, period: str = "6mo", interval: str = "1d"):
	stock = yf.Ticker(ticker)
	df = stock.history(period=period, interval=interval)
	return df

if __name__ == "__main__":
	df = get_price_history("AAPL", period="1mo")
	print(df)
	print(f"\nFetched {len(df)} rows.")
