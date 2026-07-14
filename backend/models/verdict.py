import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "data"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "analysis"))

from price_data import get_price_history
from technical import add_technical_indicators
from signals import interpret_signals
from fundamental_score import score_fundamentals
from sentiment import analyze_news_sentiment


def score_technical(df):
    latest = df.iloc[-1]
    score = 0

    price = latest["Close"]
    sma20 = latest["SMA_20"]
    sma50 = latest["SMA_50"]
    if price > sma20 > sma50:
        score += 30
        trend_direction = "up"
    elif price < sma20 < sma50:
        score -= 30
        trend_direction = "down"
    else:
        trend_direction = "sideways"

    if latest["MACD_12_26_9"] > latest["MACDs_12_26_9"]:
        score += 20
    else:
        score -= 20

    rsi = latest["RSI"]
    if rsi <= 30:
        if trend_direction == "down":
            score += 5
        else:
            score += 20
    elif rsi >= 70:
        if trend_direction == "up":
            score -= 5
        else:
            socre -= 20 

    if len(df) >= 6:
        price_5d_ago = df.iloc[-6]["Close"]
        roc_5d = ((price - price_5d_ago) / price_5d_ago) * 100

        if roc_5d <= -10:
            score -= 30
        elif roc_5d <= -5:
            score -= 15
        elif roc_5d >= 10:
            score += 30
        elif roc_5d >= 5:
            score += 15

    vol_ratio = latest["Volume_Ratio"]
    if vol_ratio >= 1.5:
        score += 10 if score > 0 else (-10 if score < 0 else 0)

    score = max(-100, min(100, score))
    return score


def score_fundamental(fund_signals):
    score = 0

    valuation = fund_signals.get("Valuation", "")
    if "Cheap" in valuation:
        score += 30
    elif "Expensive" in valuation:
        score -= 30

    profitability = fund_signals.get("Profitability", "")
    if "Above-average" in profitability:
        score += 30
    elif "Below-average" in profitability:
        score -= 30

    growth = fund_signals.get("Growth", "")
    if "Strong" in growth:
        score += 40
    elif "Declining" in growth:
        score -= 40

    score = max(-100, min(100, score))
    return score


def score_sentiment(sentiment_result):
    positive = sentiment_result["positive_pct"]
    negative = sentiment_result["negative_pct"]
    return max(-100, min(100, positive - negative))


def get_verdict(ticker, peer_tickers, from_date, to_date):
    df = get_price_history(ticker, period="6mo")
    df = add_technical_indicators(df)
    tech_signals = interpret_signals(df)
    tech_score = score_technical(df)

    fund_signals = score_fundamentals(ticker, peer_tickers)
    fund_score = score_fundamental(fund_signals)

    sentiment_result = analyze_news_sentiment(ticker, from_date, to_date)
    sent_score = score_sentiment(sentiment_result)

    weight_technical = 0.50
    weight_sentiment = 0.25
    weight_fundamental = 0.25

    composite_score = (
        tech_score * weight_technical
        + sent_score * weight_sentiment
        + fund_score * weight_fundamental
    )

    if composite_score >= 20:
        verdict = "BULLISH"
    elif composite_score <= -20:
        verdict = "BEARISH"
    else:
        verdict = "NEUTRAL"

    confidence = min(100, abs(composite_score))

    return {
        "ticker": ticker,
        "verdict": verdict,
        "confidence": round(confidence, 1),
        "composite_score": round(composite_score, 1),
        "breakdown": {
            "technical_score": tech_score,
            "fundamental_score": fund_score,
            "sentiment_score": round(sent_score, 1),
        },
        "technical_signals": tech_signals,
        "fundamental_signals": fund_signals,
        "sentiment_summary": sentiment_result["overall_sentiment"],
    }


if __name__ == "__main__":
    result = get_verdict(
        ticker="AAPL",
        peer_tickers=["MSFT", "GOOGL", "META"],
        from_date="2026-06-25",
        to_date="2026-07-08",
    )

    print(f"=== Verdict for {result['ticker']} ===")
    print(f"Verdict: {result['verdict']} (confidence: {result['confidence']}%)")
    print(f"Composite score: {result['composite_score']}\n")

    print("Score breakdown:")
    for name, value in result["breakdown"].items():
        print(f"  {name}: {value}")

    print("\nTechnical signals:")
    for name, read in result["technical_signals"].items():
        print(f"  {name}: {read}")

    print("\nFundamental signals:")
    for name, read in result["fundamental_signals"].items():
        print(f"  {name}: {read}")

    print(f"\nSentiment: {result['sentiment_summary']}")
