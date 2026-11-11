from app.services.nli_provider import LABELS, interpret_scores

def test_high_margin_support_prediction_is_returned_as_model_relation():
    relation, score = interpret_scores([
        {"label": LABELS[0], "score": 0.91},
        {"label": LABELS[1], "score": 0.04},
        {"label": LABELS[2], "score": 0.05},
    ])
    assert relation == "supports"
    assert score == 0.91

def test_high_margin_contradiction_prediction_is_returned_as_model_relation():
    relation, _ = interpret_scores([
        {"label": LABELS[0], "score": 0.03},
        {"label": LABELS[1], "score": 0.92},
        {"label": LABELS[2], "score": 0.05},
    ])
    assert relation == "contradicts"

def test_low_margin_predictions_abstain():
    relation, _ = interpret_scores([
        {"label": LABELS[0], "score": 0.48},
        {"label": LABELS[1], "score": 0.44},
        {"label": LABELS[2], "score": 0.08},
    ])
    assert relation == "uncertain"

def test_insufficient_evidence_label_is_preserved():
    relation, _ = interpret_scores([
        {"label": LABELS[0], "score": 0.08},
        {"label": LABELS[1], "score": 0.04},
        {"label": LABELS[2], "score": 0.88},
    ])
    assert relation == "insufficient"

def test_invalid_provider_output_abstains():
    assert interpret_scores([{"label": "unexpected", "score": "bad"}]) == ("uncertain", None)
