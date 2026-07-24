import sys
import os
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "data"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "analysis"))

from price_data import get_price_history
from technical import add_technical_indicators
from verdict import score_technical

def backtest_technical_signal(ticker, period="2y", holding_days=10):
	df = get_price_history(ticker, period=period)
	df = add_technical_indicators(df)
	df = df.dropna()

	results = []

	for i in range(len(df) - holding_days):
		row_df = df.iloc[:i+1]
		current_row = df.iloc[i]

		tech_score = score_technical(row_df)

		entry_price = current_row["Close"]
		future_price = df.iloc[i + holding_days]["Close"]
		future_return_pct = ((future_price - entry_price) / entry_price) * 100

		if tech_score >= 20:
			signal = "BULLISH"
		elif tech_score <= -20:
			signal = "BEARISH"
		else:
			signal = "NEUTRAL"

		results.append({
			"date": df.index[i],
			"signal": signal,
			"tech_score": tech_score,
			"future_return_pct": round(future_return_pct, 2),
		})

	return pd.DataFrame(results)

def summarize_backtest(results_df):
	summary = []
	
	for signal_type in ["BULLISH", "BEARISH", "NEUTRAL"]:
		subset = results_df[results_df["signal"] == signal_type]

		if len(subset) == 0:
			continue

		if signal_type == "BULLISH":
			wins = subset[subset["future_return_pct"] > 0]
		elif signal_type == "BEARISH":
			wins = subset[subset["future_return_pct"] < 0]
		else:
			wins = subset

		win_rate = (len(wins) / len(subset)) * 100 if signal_type != "NEUTRAL" else None
		avg_return = subset["future_return_pct"].mean()

		summary.append({
			"signal": signal_type,
			"count": len(subset),
			"win_rate_pct": round(win_rate, 1) if win_rate is not None else "N/A",
			"avg_future_return_pct": round(avg_return, 2),
		})

	return pd.DataFrame(summary)

if __name__ == "__main__":
	results = backtest_technical_signal("AAPL", period="2y", holding_days=10)
	summary = summarize_backtest(results)
	print(summary)
	print(f"\nTotal signals tested: {len(results)}")
