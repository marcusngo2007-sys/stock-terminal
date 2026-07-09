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
    """
    Converts technical signals into a numeric score from -100 (very bearish)
    to +100 (very bullish), based on simple, explainable rules.
    """
    latest = df.iloc[-1]
    score = 0

    # RSI: extreme readings contribute to score
    rsi = latest["RSI"]
    if rsi <= 30:
        score += 20   # oversold - potential bounce, bullish
    elif rsi >= 70:
        score -= 20   # overbought - potential pullback, bearish

    # MACD: trend momentum direction
    if latest["MACD_12_26_9"] > latest["MACDs_12_26_9"]:
        score += 20
    else:
        score -= 20

    # Moving average trend
    price = latest["Close"]
    sma20 = latest["SMA_20"]
    sma50 = latest["SMA_50"]
    if price > sma20 > sma50:
        score += 30
    elif price < sma20 < sma50:
        score -= 30

    # Volume confirmation - high volume strengthens whatever
    # direction the trend is already pointing
    vol_ratio = latest["Volume_Ratio"]
    if vol_ratio >= 1.5:
        score += 10 if score > 0 else (-10 if score < 0 else 0)

    # Clamp score to -100/+100 range just in case
    score = max(-100, min(100, score))
    return score


def score_fundamental(fund_signals):
    """
    Converts fundamental signal text into a numeric score, -100 to +100.
    """
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
    """
    Converts sentiment percentages into a numeric score, -100 to +100.
    """
    positive = sentiment_result["positive_pct"]
    negative = sentiment_result["negative_pct"]
    return max(-100, min(100, positive - negative))


def get_verdict(ticker, peer_tickers, from_date, to_date):
    """
    Combines technical, fundamental, and sentiment scores into
    one overall weighted verdict.
    """
    # Gather all underlying analysis
    df = get_price_history(ticker, period="6mo")
    df = add_technical_indicators(df)
    tech_signals = interpret_signals(df)
    tech_score = score_technical(df)

    fund_signals = score_fundamentals(ticker, peer_tickers)
    fund_score = score_fundamental(fund_signals)

    sentiment_result = analyze_news_sentiment(ticker, from_date, to_date)
    sent_score = score_sentiment(sentiment_result)

    # Weights - adjustable in one place
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
