import pandas as pd
import numpy as np
from scipy.signal import argrelextrema

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "data"))
from price_data import get_price_history

def find_swing_points(df: pd.DataFrame, order: int = 5):
	highs = df["High"].values
	lows = df["Low"].values

	high_idx = argrelextrema(highs, np.greater, order=order)[0]
	low_idx = argrelextrema(lows, np.less, order=order)[0]

	swing_highs = df.iloc[high_idx][["High"]].rename(columns={"High": "price"})
	swing_lows = df.iloc[low_idx][["Low"]].rename(columns={"Low": "price"})

	return swing_highs, swing_lows

def cluster_levels(swing_points: pd.DataFrame, tolerance_pct: float = 0.02):
	if swing_points.empty:
		return[]

	prices = sorted(swing_points["price"].tolist())
	zones = []
	current_zone = [prices[0]]	

	for price in prices[1:]:
		if abs(price - np.mean(current_zone)) / np.mean(current_zone) <= tolerance_pct: 
			current_zone.append(price)
		else:
			zones.append(current_zone)
			current_zone = [price]
	zones.append(current_zone)
		
	zone_summary = [
		{"level": round(np.mean(z), 2), "touches": len(z)}
		for z in zones
	]

	zone_summary.sort(key=lambda x: x["touches"], reverse=True)

	return zone_summary

def get_support_resistance(ticker: str, period: str = "6mo"):
	df = get_price_history(ticker, period=period)
	swing_highs, swing_lows = find_swing_points(df)

	resistance_zones = cluster_levels(swing_highs)
	support_zones = cluster_levels(swing_lows)

	return {
		"resistance": resistance_zones,
		"support": support_zones,
	}

if __name__ == "__main__":
	levels = get_support_resistance("AAPL")

	print("Resistance zones (price, times touched):")
	for zone in levels["resistance"][:5]:
		print(f" ${zone["level"]} - touched {zone["touches"]}x")

	print("\nSupport zones (price, times touched):")
	for zone in levels["support"][:5]:
		print(f" ${zone["level"]} - touched {zone["touches"]}x")
