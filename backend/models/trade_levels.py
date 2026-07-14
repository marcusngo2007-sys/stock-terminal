import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "data"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "analysis"))

from price_data import get_price_history
from technical import add_technical_indicators
from support_resistance import get_support_resistance

def get_trade_levels(ticker, verdict, current_position_entry=None):
	df = get_price_history(ticker, period="6mo")
	df = add_technical_indicators(df)
	latest = df.iloc[-1]

	current_price = latest["Close"]
	atr = latest["ATR"]

	levels = get_support_resistance(ticker)
	supports = sorted([z["level"] for z in levels["support"]], reverse=True)
	resistances = sorted([z["level"] for z in levels["resistance"]])

	nearest_support = next((s for s in supports if s < current_price), None)
	nearest_resistance = next((r for r in resistances if r > current_price), None)

	result = {
		"ticker": ticker, 
		"current_price": round(current_price, 2),
		"atr": round(atr, 2),
		"nearest_support": nearest_support,
		"nearest_resistance": nearest_resistance,
	}

	if current_position_entry is not None:
		unrealized_pct = ((current_price - current_position_entry) / current_position_entry) * 100

		atr_stop = current_price - (1.5 * atr)
		stop_loss = max(atr_stop, nearest_support)

		if unrealized_pct > 10:
			breakeven_plus = current_position_entry + ((current_price - current_position_entry) * 0.5)
			stop_loss = max(stop_loss, breakeven_plus)

		risk = current_price - stop_loss
		rr_target = current_price + (2 * risk)
		take_profit = nearest_resistance if nearest_resistance else rr_target
		
		if verdict == "BEARISH" and unrealized_pct > 0:
			action = "Consider taking profits"
			note = f"You're up {unrealized_pct:.1f}%, but the verdict has turned bearish. Consider locking in gains rather than risking a reversal."
		elif verdict == "BEARISH" and unrealized_pct <= 0:
			action = "Consider cutting losses"
			note = f"You're down {abs(unrealized_pct):.1f}% and the verdict is bearish. Consider exiting near your stop-loss to limit further downside."
		elif verdict == "BULLISH":
			action = "Consider holding"
			note = f"Verdict remains bullish. Current position is {'up' if unrealized_pct >= 0 else 'down'} {abs(unrealized_pct):.1f}%. Stop-loss and take-profit levels below."
		else:
			action = "Hold and monitor"
			note = f"Mixed signals. Current position is {'up' if unrealized_pct >= 0 else 'down'} {abs(unrealized_pct):.1f}%. No strong conviction either way right now."

		result.update({
			"position_entry": current_position_entry,
			"unrealized_pct": round(unrealized_pct, 2),
			"action": action,
			"suggested_stop_loss": round(stop_loss, 2),
			"suggested_take_profit": round(take_profit, 2),
			"take_profit_below_entry": take_profit < current_position_entry,
			"note": note,
		})

	else:
		if verdict == "BULLISH":
			suggested_entry = nearest_support if nearest_support else current_price
			atr_stop = suggested_entry - (1.5 * atr)
			stop_loss = max(atr_stop, nearest_support * 0.98) if nearest_support else atr_stop
			risk = suggested_entry - stop_loss
			
			if nearest_resistance:
				take_profit = nearest_resistance

			else:
				fallback_target = current_price + (2 * risk)
				take_profit = max(fallback_target, current_price * 1.02)
	
			extended = ((current_price - suggested_entry) / suggested_entry) * 100 if suggested_entry else 0

			if extended > 3:
				action = "Wait for pullback before entering"
				note = f"Price is {extended:.1f}% above suggested entry zone. Bullish setup, but entering now means chasing an extended move."
			else:
				action = "Consider entering"
				note = "Price is near the suggested entry zone."

			result.update({
				"action": action,
				"suggested_entry_zone": round(suggested_entry, 2),
				"suggested_stop_loss": round(stop_loss, 2),
				"suggested_take_profit": round(take_profit, 2),
				"note": note,
			})

		elif verdict == "BEARISH":
			result.update({
				"action": "Avoid entering long positions",
				"note": "Bearish signals suggest waiting for trend reversal before considering a long entry",
			})

		else:
			result.update({
				"action": "Wait for clearer signal",
				"note": "Mixed signals - consider waiting for stronger conviction before entering",
			})

	return result

if __name__ == "__main__":
	result = get_trade_levels("AAPL", verdict="BULLISH")
	print("=== No position (hypothetical BULLISH verdict) ===")
	for key, value in result.items():
		print(f"{key}: {value}")

	print()

	result2 = get_trade_levels("AAPL", verdict="NEUTRAL", current_position_entry=195.00)
	print("=== Existing position (entered at $195) ===")
	for key, value in result2.items():
		print(f"{key}: {value}") 
