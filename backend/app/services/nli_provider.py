"""Optional MNLI zero-shot assessment over retrieved evidence snippets.

Outputs are model relations, not factual verdicts. Low-margin predictions
abstain. The provider is opt-in because inference incurs external cost and
requires a Hugging Face Inference Providers token.
"""
import logging
import requests
from app.core.config import get_settings

logger = logging.getLogger(__name__)
MODEL_ID = "facebook/bart-large-mnli"
ENDPOINT = "https://router.huggingface.co/hf-inference/models/facebook/bart-large-mnli"
LABELS = ("supports the claim", "contradicts the claim", "does not provide enough information to assess the claim")

class NLIProviderError(RuntimeError):
    pass

def interpret_scores(scores: list[dict], minimum_score: float = 0.75, minimum_margin: float = 0.15) -> tuple[str, float | None]:
    normalized = []
    for item in scores:
        label = str(item.get("label", "")).strip().lower()
        try:
            score = float(item.get("score"))
        except (TypeError, ValueError):
            continue
        if 0.0 <= score <= 1.0:
            normalized.append((label, score))
    normalized.sort(key=lambda item: item[1], reverse=True)
    if not normalized:
        return "uncertain", None
    top_label, top_score = normalized[0]
    second_score = normalized[1][1] if len(normalized) > 1 else 0.0
    if top_label == LABELS[2]:
        return "insufficient", top_score
    if top_score < minimum_score or top_score - second_score < minimum_margin:
        return "uncertain", top_score
    if top_label == LABELS[0]:
        return "supports", top_score
    if top_label == LABELS[1]:
        return "contradicts", top_score
    return "uncertain", top_score

class HuggingFaceNLIProvider:
    def assess(self, claim: str, evidence: str) -> dict | None:
        token = get_settings().huggingface_api_token
        if not token:
            return None
        if not evidence.strip():
            return {"relation": "insufficient", "score": None, "model_id": MODEL_ID}
        try:
            response = requests.post(
                ENDPOINT,
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json={
                    "inputs": evidence[:3000],
                    "parameters": {
                        "candidate_labels": list(LABELS),
                        "hypothesis_template": f"The evidence passage {{}} the following claim: {claim[:800]}",
                        "multi_label": False,
                    },
                },
                timeout=(2.0, 6.0),
            )
            response.raise_for_status()
            payload = response.json()
        except (requests.RequestException, ValueError) as exc:
            logger.warning("NLI inference failed: %s", type(exc).__name__)
            raise NLIProviderError("Evidence assessment is temporarily unavailable") from exc
        if isinstance(payload, dict) and payload.get("error"):
            raise NLIProviderError("Evidence assessment model is unavailable")
        if not isinstance(payload, list):
            raise NLIProviderError("Evidence assessment returned an unexpected response")
        relation, score = interpret_scores(payload)
        return {"relation": relation, "score": score, "model_id": MODEL_ID}

nli_provider = HuggingFaceNLIProvider()
