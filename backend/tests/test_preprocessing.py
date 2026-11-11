from app.services.text_preprocessing import normalize_text

def test_normalize_text_matches_expected_training_contract():
    assert normalize_text("THE QUICK, Brown foxes!") == "quick brown foxes"

def test_normalize_text_collapses_whitespace():
    assert normalize_text("A\n\nclaim   about facts") == "claim facts"
