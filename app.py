import streamlit as st
import sys
import os
import plotly.graph_objects as go
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), "backend", "data"))
sys.path.append(os.path.join(os.path.dirname(__file__), "backend", "analysis"))
sys.path.append(os.path.join(os.path.dirname(__file__), "backend", "models"))

from price_data import get_price_history
from technical import add_technical_indicators
from full_analysis import get_full_analysis
from sentiment import analyze_news_sentiment
from datetime import datetime
from fundamental_score import get_peer_comparison_table
from full_analysis import get_watchlist_summary

st.set_page_config(page_title="Mini Bloomberg Terminal", layout="wide")

st.title("Mini Bloomberg Terminal")

col1, col2, col3 = st.columns([2, 2, 1])
with col1:
	ticker = st.text_input("Ticker symbol", value = "AAPL")
with col2:
	has_position = st.checkbox("I already own this stock")
	position_entry = None
	if has_position:
		position_entry = st.number_input("Your entry price", min_value=0.0, value=100.0, step=0.01)
with col3:
	st.write("")
	analyze_clicked = st.button("Analyze", use_container_width = True)

with st.sidebar:
	st.subheader("Watchlist")
	watchlist_input = st.text_input("Tickers (comma-separated)", value = "AAPL, MSFT, TSLA, NVDA")
	watchlist_clicked = st.button("Load Watchlist")

	if watchlist_clicked:
		tickers_list = [t.strip().upper() for t in watchlist_input.split(",")]
		with st.spinner("Loading watchlist..."):
			watchlist_data = get_watchlist_summary(
				tickers_list,
				peer_tickers = ["MSFT", "GOOGL", "META"],
				from_date = "2026-06-25",
				to_date = "2026-07-08",
			)
		watchlist_df = pd.DataFrame(watchlist_data)
		st.dataframe(watchlist_df, use_container_width=True, hide_index=True)

if analyze_clicked:
	try:
		with st.spinner(f"Analyzing {ticker}..."):	
			df = get_price_history(ticker, period="6mo")
			df = add_technical_indicators(df)
		
			result = get_full_analysis(
				ticker = ticker,
				peer_tickers = ["MSFT", "GOOGL", "META"],
				from_date = "2026-06-25",
				to_date = "2026-07-08",
				position_entry = position_entry,
			)
			fetch_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

		verdict = result["verdict"]
		trade = result["trade_levels"]

		verdict_color = {
			"BULLISH": "green",
			"BEARISH": "red",
			"NEUTRAL": "gray",
		}.get(verdict["verdict"], "gray")

		st.markdown(f"## Verdict: :{verdict_color}[{verdict['verdict']}]")
		confidence_value = verdict["confidence"]
		st.progress(min(int(confidence_value), 100), text=f"Confidence: {confidence_value}%")
		
		st.caption(f"Data fetched at {fetch_time}. Prices may be delayed.")

		m1, m2, m3, m4 = st.columns(4)
		m1.metric("Current Price", f"${trade['current_price']}")
		m2.metric("Nearest Support", f"${trade['nearest_support']}" if trade['nearest_support'] else "N/A")
		m3.metric("Nearest Resistance", f"${trade['nearest_resistance']}" if trade['nearest_resistance'] else "N/A")
		m4.metric("ATR (Volatility)", f"${trade['atr']}")

		st.subheader("Price Chart")
		fig = go.Figure()
		fig.add_trace(go.Candlestick(
			x = df.index, open = df["Open"], high = df["High"],
			low = df["Low"], close = df["Close"], name = "Price"
		))
		fig.add_trace(go.Scatter(x=df.index, y=df["SMA_20"], name="SMA 20", line=dict(width=1)))
		fig.add_trace(go.Scatter(x=df.index, y=df["SMA_50"], name="SMA 50", line=dict(width=1)))
		fig.update_layout(height=500, xaxis_rangeslider_visible=False)
		st.plotly_chart(fig, use_container_width=True)

		col_tech, col_fund = st.columns(2)
		with col_tech:
			st.subheader("Technical Signals")
			for name, read in verdict["technical_signals"].items():
				st.write(name + ": " + str(read))
	
		with col_fund:
			st.subheader("Fundamental Signals")
			for name, read in verdict["fundamental_signals"].items():
				st.write(name + ": " + str(read))

		st.subheader("Peer Comparison")
		peer_table = get_peer_comparison_table(ticker, ["MSFT", "GOOGL", "META"])
		peer_df = pd.DataFrame(peer_table)
		st.dataframe(peer_df, use_container_width=True, hide_index=True)	

		st.subheader("News Sentiment")
		st.write(verdict["sentiment_summary"])

		news_result = analyze_news_sentiment(ticker, "2026-06-25", "2026-07-08")

		col_pos, col_neg, col_neu = st.columns(3)
		col_pos.metric("Positive", f"{news_result['positive_pct']}%")
		col_neg.metric("Negative", f"{news_result['negative_pct']}%")
		col_neu.metric("Neutral", f"{news_result['neutral_pct']}%")

		st.write("**Recent headlines:**")
		for item in news_result["sample_headlines"]:
			sentiment_emoji = {
				"positive": "🟢",
				"negative": "🔴",
				"neutral": "⚪",
			}.get(item["sentiment"], "⚪")
			st.write(sentiment_emoji + " " + item["headline"])

		st.subheader("Trade Levels")
		if "suggested_entry_zone" in trade:
			t1, t2, t3 = st.columns(3)
			t1.metric("Suggested Entry", f"${trade['suggested_entry_zone']}")
			t2.metric("Stop Loss", f"${trade['suggested_stop_loss']}")
			t3.metric("Take Profit", f"${trade['suggested_take_profit']}")
			st.info(trade.get("note", ""))

		elif "position_entry" in trade:
			st.write("Recommendation: " + trade.get("action", ""))
			t1, t2, t3 = st.columns(3)
			t1.metric("Unrealized P&L", f"{trade['unrealized_pct']}%")
			t2.metric("Stop Loss", f"${trade['suggested_stop_loss']}")
			t3.metric("Take Profit", f"${trade['suggested_take_profit']}")
			if trade.get("take_profit_below_entry"):
				st.warning("Note: this take-profit target is a near-term technical level and is still below your original entry price. Reaching it would reduce your loss, not create a profit.")
			st.info(trade.get("note", ""))
		else:
			st.write(trade.get("action", ""))
			st.write(trade.get("note", ""))

	except ValueError as e:
		st.error(str(e))
