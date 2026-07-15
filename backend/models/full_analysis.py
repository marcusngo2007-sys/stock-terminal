import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "data"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "analysis"))

from verdict import get_verdict
from trade_levels import get_trade_levels

def get_full_analysis(ticker, peer_tickers, from_date, to_date, position_entry=None):
	verdict_result = get_verdict(ticker, peer_tickers, from_date, to_date)
	trade_result = get_trade_levels(ticker, verdict_result["verdict"], position_entry)

	return {
		"verdict": verdict_result,
		"trade_levels": trade_result,
	}

if __name__ == "__main__":
	result = get_full_analysis(
		ticker = "AAPL",
		peer_tickers = ["MSFT", "GOOGL", "META"],
		from_date = "2026-06-25",
		to_date = "2026-07-08",
	)

	print("VERDICT:")
	print(result["verdict"]["verdict"], "-", result["verdict"]["confidence"], "%")

	print("\nTRADE LEVELS:")
	for key, value in result["trade_levels"].items():
		print(f" {key}: {value}")

def get_watchlist_summary(tickers, peer_tickers, from_date, to_date):
	summary = []
	
	for t in tickers:
		try:
			result = get_verdict(t, peer_tickers, from_date, to_date)
			trade = get_trade_levels(t, result["verdict"])

			summary.append({
				"Ticker": t,
				"Price": trade["current_price"],
				"Verdict": result["verdict"],
				"Confidence": result["confidence"],
			})
		except ValueError:
			summary.append({
				"Ticker": t,
				"Price": None,
				"Verdict": "N/A",
				"Confidence": None,
			})
	return summary
