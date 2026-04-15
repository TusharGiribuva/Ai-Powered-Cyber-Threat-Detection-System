import re
import urllib.parse
from core.model_loader import predict_url


def rule_based_score(text: str):
    score = 0
    notes = []

    if re.search(r"(?i)(union\s+select|or\s+1=1)", text):
        score += 20
        notes.append("SQL Injection")

    if re.search(r"(?i)<script|javascript:", text):
        score += 20
        notes.append("XSS")

    if text.startswith("http"):
        parsed = urllib.parse.urlparse(text)

        if parsed.scheme != "https":
            score += 10
            notes.append("Not HTTPS")

        if re.match(r"\d+\.\d+\.\d+\.\d+", parsed.netloc):
            score += 25
            notes.append("IP used")

    return score, notes


def analyze_payload(text: str):
    is_url = text.startswith("http")

    rule_score, notes = rule_based_score(text)
    ml_score = predict_url(text) if is_url else 0

    final_score = (0.7 * ml_score) + (0.3 * rule_score)

    if final_score > 75:
        severity = "critical"
    elif final_score > 50:
        severity = "high"
    elif final_score > 30:
        severity = "medium"
    else:
        severity = "low"

    return {
        "threat_score": round(final_score, 2),
        "ml_score": round(ml_score, 2),
        "rule_score": round(rule_score, 2),
        "severity": severity,
        "indicators": notes,
        "feature_contributions": [],
        "mitigations": ["Monitor traffic", "Block suspicious activity"],
        "model": "hybrid-v1"
    }