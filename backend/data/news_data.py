import os
import requests
from dotenv import load_dotenv

load_dotenv()

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")

def get_company_news(ticker: str, from_date: str, to_date: str):
	url = "https://finnhub.io/api/v1/company-news"
	params = {
		"symbol": ticker,
		"from": from_date,
		"to": to_date,
		"token": FINNHUB_API_KEY,
	}
	
	response = requests.get(url, params=params)
	response.raise_for_status()
	return response.json()

if __name__ == "__main__":
	news = get_company_news("AAPL", "2026-06-25", "2026-07-03")
	print(f"Found {len(news)} articles.\n")

	for article in news[:5]:
		print(article["headline"])
		print(article["url"])
		print("---")
