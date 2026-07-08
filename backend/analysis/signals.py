import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "data"))
from price_data import get_price_history
from technical import add_technical_indicators

def interpret_signals(df):
	latest = df.iloc[-1]
	signals = {}

	rsi = latest["RSI"]
	if rsi >= 70:
		signals["RSI"] = f"Overbought ({rsi:.1f})"
	elif rsi <= 30:
		signals["RSI"] = f"Oversold ({rsi:.1f})"
	else:
		signals["RSI"] = f"Neutral ({rsi:.1f})"

	macd_line = latest["MACD_12_26_9"]
	macd_signal = latest["MACDs_12_26_9"]
	if macd_line > macd_signal:
		signals["MACD"] = "Bullish (MACD above signal line)"
	else:
		signals["MACD"] = "Bearish (MACD below signal line)"

	price = latest["Close"]
	sma20 = latest["SMA_20"]
	sma50 = latest["SMA_50"]
	if price > sma20 > sma50:
		signals["Trend"] = "Strong uptrend (price > SMA20 > SMA50)"
	elif price < sma20 < sma50: 
		signals["Trend"] = "Strong downtrend (price < SMA20 < SMA50)"
	else:
		signals["Trend"] = "Mixed/sideways trend"

	vol_ratio = latest["Volume_Ratio"]
	if vol_ratio >= 1.5:
		signals["Volume"] = f"High volume ({vol_ratio:.2f}x average) - strong interest"
	elif vol_ratio <= 0.5:
		signals["Volume"] = f"LOw volume ({vol_ratio:.2f}x average) - weak participation"
	else:
		signals["Volume"] = f"Normal volume ({vol_ratio:.2f}x average)"

	atr_pct = (latest["ATR"] / price) * 100
	if atr_pct >= 3:
		signals["Volatility"] = f"High ({atr_pct:.2f}% of price)"
	elif atr_pct <= 1:
		signals["Volatility"] = f"Low ({atr_pct:.2f}% of price)"
	else:
		signals["Volatility"] = f"Moderate ({atr_pct:.2f}% of price)"

	return signals

if __name__ == "__main__":
	df = get_price_history("AAPL", period="6mo")
	df = add_technical_indicators(df)
	signals = interpret_signals(df)

	print("Technical Signal Summary for AAPL:\n")
	for name, read in signals.items():
		print(f"{name}: {read}")
