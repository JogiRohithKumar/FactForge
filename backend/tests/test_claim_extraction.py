from app.services.claim_extraction import extract_claim_candidates

def test_extracts_unique_sentence_candidates():
    text = "The city council approved the proposal after a public meeting. The city council approved the proposal after a public meeting. This sentence is also long enough to be a candidate claim."
    result = extract_claim_candidates(text)
    assert len(result) == 2
    assert result[0].startswith("The city council")
