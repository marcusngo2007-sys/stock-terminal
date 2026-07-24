# Mini Bloomberg Terminal

A stock analysis tool that pulls price, news, and fundamental data for any ticker and gives a bullish/bearish/neutral verdict, along with suggested entry, stop-loss, and take-profit levels.

## What it does

- Verdict (Bullish/Bearish/Neutral) combining technical indicators, fundamentals vs. peers, and news sentiment
- RSI, MACD, moving averages, Bollinger Bands, ATR, volume trends
- Support/resistance zones from price history
- FinBERT-based sentiment analysis on recent news headlines
- Suggested stop-loss/take-profit, with different logic depending on whether you already hold a position
- Peer comparison table + a small watchlist view

## How the verdict works

Technical, fundamental, and sentiment signals are each scored from -100 to +100 using explicit rules (not ML), then combined with fixed weights: 50% technical, 25% fundamental, 25% sentiment. I went with rules over a model mainly because I wanted every verdict to be traceable — you can look at the breakdown and see exactly which signals pushed it bullish or bearish.
One thing I had to fix along the way: my first version treated oversold RSI as automatically bullish. Turns out that's wrong — a stock in a real downtrend is often oversold too, and treating that as bullish was cancelling out otherwise correct bearish signals. Fixed it so RSI only counts as a reversal signal when it's not fighting the existing trend. Also added a short-term (5-day) price change check, since moving averages are slow to react to sharp drops.

## Limitations

- Price data is delayed ~15-20 min (free tier), not real-time
- Fundamentals only update quarterly, obviously

- No real order book / Level 2 data — "volume" analysis is just daily volume, not live order flow
- Peer groups for comparison are hardcoded per ticker, not auto-selected by sector
- This is a learning project, not financial advice

## Stack

Python throughout. yfinance + Finnhub for data, pandas/pandas-ta for indicators, FinBERT for sentiment, Streamlit + Plotly for the frontend.

