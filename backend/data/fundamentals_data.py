import yfinance as yf

def get_fundamentals(ticker: str):
	stock = yf.Ticker(ticker)
	info = stock.info

	fundamentals = {
		"name": info.get("longName"),
		"sector": info.get("sector"),
		"industry": info.get("industry"),
		"market_cap": info.get("marketCap"),
		"pe_ratio": info.get("trailingPE"),
		"forward_pe": info.get("forwardPE"),
		"pb_ratio": info.get("priceToBook"),
		"eps": info.get("trailingEps"),
		"dividend_yield": f"{info.get("dividendYield")}%",
		"profit_margin": info.get("profitMargins"),
		"revenue_growth": info.get("revenueGrowth"),
		"debt_to_equity": info.get("debtToEquity"),
		"52_week_high": info.get("fiftyTwoWeekHigh"),
		"52_week_low": info.get("fiftyTwoWeekLow"),
	}

	return fundamentals

if __name__ == "__main__":
	data = get_fundamentals("AAPL")
	for key, value in data.items():
		print(f"{key}: {value}")
