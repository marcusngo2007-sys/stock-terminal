import streamlit as st
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "backend", "data"))
sys.path.append(os.path.join(os.path.dirname(__file__), "backend", "analysis"))
sys.path.append(os.path.join(os.path.dirname(__file__), "backend", "models"))

from full_analysis import get_full_analysis

st.title("Mini Bloomberg Terminal")
st.write("Enter a stock ticker to get a full analysis.")

ticker = st.text_input("Ticker symbol", value="AAPL")

if st.button("Analyze"):
	st.write(f"Analyzing {ticker}...")

	result = get_full_analysis(
		ticker=ticker,
		peer_tickers=["MSFT", "GOOGL", "META"],
		from_date="2026-06-25",
		to_date="2026-07-08",
	)

	st.subheader("Verdict")
	st.write(result['verdict']['verdict'])
	st.write(f"Confidence: {result['verdict']['confidence']}%")

	st.subheader("Trade Levels")
	st.json(result["trade_levels"])
