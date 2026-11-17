from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

OUTAGE_KEYWORDS = {"down", "outage", "crash", "crashed", "offline", "unavailable", "500", "502", "503"}
PERFORMANCE_KEYWORDS = {"slow", "latency", "timeout", "lag", "lagging", "freeze", "freezing", "error"}
BILLING_KEYWORDS = {"invoice", "billing", "charge", "charged", "refund", "payment", "subscription"}


def analyze_ticket(text: str) -> dict:
    """
    Evaluates ticket sentiment, category, and normalized urgency score (0.00 - 1.00).
    Decoupled from Flask/HTTP so the NLP engine can evolve independently.
    """
    scores = analyzer.polarity_scores(text)
    compound = scores["compound"]

    # Map VADER compound score (-1.0 to +1.0) to sentiment label
    if compound >= 0.05:
        sentiment = "Positive"
    elif compound <= -0.05:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"

    # Base urgency derived from negative sentiment intensity (0.00 to 1.00)
    base_urgency = round(max(0.0, -compound), 2)

    lowered = text.lower()
    words = set(lowered.replace(".", " ").replace(",", " ").split())

    # Category detection & domain urgency guardrails
    if words & OUTAGE_KEYWORDS:
        category = "Technical_Outage"
        # Polite Emergency Safeguard: guarantees >= 0.85 even if tone is polite/neutral
        urgency_score = round(min(1.0, max(0.85, base_urgency + 0.30)), 2)
    elif words & PERFORMANCE_KEYWORDS:
        category = "Performance_Issue"
        urgency_score = round(min(1.0, base_urgency + 0.25), 2)
    elif words & BILLING_KEYWORDS:
        category = "Billing_Inquiry"
        urgency_score = round(min(1.0, base_urgency + 0.10), 2)
    else:
        category = "General_Inquiry"
        urgency_score = base_urgency

    return {
        "category": category,
        "urgency_score": urgency_score,
        "sentiment": sentiment,
        "model_version": "v1.0.0-vader",
    }