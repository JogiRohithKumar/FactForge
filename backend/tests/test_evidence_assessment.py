from app.services.evidence_assessment import classify_review_rating

def test_false_rating_is_mapped_to_publisher_stance():
    assert classify_review_rating("Pants on Fire") == "reviewer_rates_claim_false"

def test_mixed_rating_abstains_from_binary_verdict():
    assert classify_review_rating("Half True") == "reviewer_rates_claim_mixed"
    assert classify_review_rating("Mostly False") == "reviewer_rates_claim_mixed"

def test_unknown_rating_abstains():
    assert classify_review_rating("Needs more context") == "reviewer_rates_claim_mixed"
    assert classify_review_rating("Unrated") == "mixed_or_unclear"
    assert classify_review_rating(None) == "mixed_or_unclear"

def test_binary_true_rating_is_attributed_to_publisher():
    assert classify_review_rating("True") == "reviewer_rates_claim_true"
