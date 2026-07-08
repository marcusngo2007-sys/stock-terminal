from transformers import pipeline

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "data"))
from news_data import get_company_news

sentiment_pipeline = pipeline("sentiment-analysis", model="ProsusAI/finbert")

def analyze_news_sentiment(ticker: str, from_date: str, to_date: str):
	articles = get_company_news(ticker, from_date, to_date)

	if not articles:
		return {
			"overall_sentiment": "No news found", 
			"positive_pct": 0,
			"negative_pct": 0,
			"neutral_pct": 0,
			"sample_headlines": [],
		}

	headlines = [article["headline"] for article in articles if article.get("headline")]

	results = sentiment_pipeline(headlines)

	positive = sum(1 for r in results if r["label"] == "positive")
	negative = sum(1 for r in results if r["label"] == "negative")
	neutral = sum(1 for r in results if r["label"] == "neutral")
	total = len(results)

	positive_pct = (positive / total) * 100
	negative_pct = (negative / total) * 100	
	neutral_pct = (neutral / total) * 100

	if positive_pct - negative_pct >= 15:
		overall = "Bullish news sentiment"
	elif negative_pct - positive_pct >= 15:
		overall = "Bearish news sentiment"
	else:
		overall = "Mixed / Neutral news sentiment"

	sample = [
		{"headline": h, "sentiment": r["label"], "confidence": round(r["score"], 2)}
		for h, r in zip(headlines[:5], results[:5])
	]

	return {
		"overall_sentiment": overall,
		"positive_pct": round(positive_pct, 1),
		"negative_pct": round(negative_pct, 1),
		"neutral_pct": round(neutral_pct, 1),
		"sample_headlines": sample,
	}

if __name__ == "__main__":
	result = analyze_news_sentiment("AAPL", "2026-06-25", "2026-07-08")
	
	print(f"Overall: {result["overall_sentiment"]}")
	print(f"Positive: {result["positive_pct"]}% | Negative: {result["negative_pct"]}% | Neutral: {result["neutral_pct"]}%\n")

	print("Sample headlines:")
	for item in result["sample_headlines"]:
		print(f" [{item["sentiment"]} ({item["confidence"]})] {item["headline"]}")	


