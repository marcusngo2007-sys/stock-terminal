import pandas as pd
import pandas_ta as ta

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "data"))
from price_data import get_price_history

def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
	df["RSI"] = df.ta.rsi(length=14)

	macd = df.ta.macd(fast=12, slow=26, signal=9)
	df = pd.concat([df, macd], axis=1)

	df["SMA_20"] = df.ta.sma(length=20)
	df["SMA_50"] = df.ta.sma(length=50)

	bbands = df.ta.bbands(length=20, std=2)
	df = pd.concat([df, bbands], axis=1)

	df["ATR"] = df.ta.atr(length=14)

	df["OBV"] = df.ta.obv()

	df["Volume_SMA_20"] = df.ta.sma(close=df["Volume"], length=20)
	df["Volume_Ratio"] = df["Volume"] / df["Volume_SMA_20"]
	
	return df

if __name__ == "__main__":
	df = get_price_history("AAPL", period="6mo")
	df = add_technical_indicators(df)

	print(df[["Close", "RSI", "SMA_20", "SMA_50", "ATR", "Volume_Ratio"]].tail())
