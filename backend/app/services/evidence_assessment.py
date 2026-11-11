"""Conservative mapping of a publisher's textual rating to attributed stance."""
import re

def classify_review_rating(rating: str | None) -> str:
    if not rating:
        return "mixed_or_unclear"
    value = re.sub(r"[^a-z0-9 ]", " ", rating.lower())
    value = re.sub(r"\s+", " ", value).strip()
    mixed = ("mostly true", "half true", "partly true", "partially true", "mostly false", "partly false", "not entirely true", "not entirely false", "mixture", "mixed", "needs context", "more context", "out of context")
    if any(term in value for term in mixed):
        return "reviewer_rates_claim_mixed"
    if any(term in value for term in ("pants on fire", "false", "incorrect", "not true", "fabricated", "hoax", "misleading")):
        return "reviewer_rates_claim_false"
    if any(term in value for term in ("true", "correct", "accurate", "verified")):
        return "reviewer_rates_claim_true"
    return "mixed_or_unclear"
