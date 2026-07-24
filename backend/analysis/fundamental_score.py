import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "data"))
from fundamentals_data import get_fundamentals

def get_peer_comparison_table(ticker, peer_tickers):	
	all_tickers = [ticker] + peer_tickers
	rows = []

	for t in all_tickers:
		data = get_fundamentals(t)
		rows.append({
			"Ticker": t,
			"P/E": data["pe_ratio"],
			"Profit Margin": f"{data['profit_margin']*100:.1f}%" if data["profit_margin"] else "N/A",
			"Revenue Growth": f"{data['revenue_growth']*100:.1f}%" if data["revenue_growth"] else "N/A",
			"Market Cap": f"${data['market_cap']/1e12:.2f}T" if data["market_cap"] and data["market_cap"] >= 1e12 else f"${data['market_cap']/1e9:.1f}B" if data["market_cap"] else "N/A",
		})

	return rows

def score_fundamentals(ticker: str, peer_tickers: list):
	target = get_fundamentals(ticker)
	peers = [get_fundamentals(t) for t in peer_tickers]
	
	peer_pes = [p["pe_ratio"] for p in peers if p["pe_ratio"] is not None]
	avg_peer_pe = sum(peer_pes) / len(peer_pes) if peer_pes else None
	
	peer_margins = [p["profit_margin"] for p in peers if p["profit_margin"] is not None]
	avg_peer_margin = sum(peer_margins) / len(peer_margins) if peer_margins else None

	signals = {}

	if target["pe_ratio"] is not None and avg_peer_pe is not None:
		diff_pct = ((target["pe_ratio"] - avg_peer_pe) / avg_peer_pe) * 100
		threshold_low = 0 - 15
		threshold_high = 15
		if diff_pct <= threshold_low:
			signals["Valuation"] = f"Cheap vs peers (P/E {target['pe_ratio']:.1f} vs avg {avg_peer_pe:.1f})"
		elif diff_pct >= threshold_high:
		   	signals["Valuation"] = f"Expensive vs peers (P/E {target['pe_ratio']:.1f} vs avg {avg_peer_pe:.1f})"
		else:
			signals["Valuation"] = f"Fairly valued vs peers (P/E {target['pe_ratio']:.1f} vs avg {avg_peer_pe:.1f})"
	else:
		signals["Valuation"] = "Not enough data to compare"
	
	if target["profit_margin"] is not None and avg_peer_margin is not None:
		if target["profit_margin"] > avg_peer_margin:
			signals["Profitability"] = f"Above-average margins ({target['profit_margin']*100:.1f}% vs peer avg {avg_peer_margin*100:.1f}%)"
		else:
			signals["Profitability"] = f"Below-average margins ({target['profit_margin']*100:.1f}% vs peer avg {avg_peer_margin*100:.1f}%)"
	else:
		signals["Profitability"] = "Not enough data to compare"

	growth = target["revenue_growth"]
	if growth is not None:
		growth_threshold_high = 15 / 100
		if growth >= growth_threshold_high:
			signals["Growth"] = f"Strong revenue growth ({growth*100:.1f}%)"
		elif growth <= 0:
			signals["Growth"] = f"Declining revenue ({growth*100:.1f}%)"
		else:
			signals["Growth"] = f"Modest revenue growth ({growth*100:.1f}%)"
	else:
		signals["Growth"] = "Not available"

	return signals


if __name__ == "__main__":
	ticker = "AAPL"
	peers = ["MSFT", "GOOGL", "META"]

	result = score_fundamentals(ticker, peers)
	
	print(f"Fundamental Analysis for {ticker} (vs {', '.join(peers)}):")	
	for name, read in result.items():
		print(f"{name}: {read}")
