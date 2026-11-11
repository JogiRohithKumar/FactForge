from app.services.research_provider import classify_domain

def test_official_domain_is_only_a_potential_official_source():
    assert classify_domain("https://data.gov.in/dataset/example") == "potential_official_source"

def test_commercial_domain_is_not_marked_official():
    assert classify_domain("https://example.com/report") == "other_publisher"
