"""Evidence-aware analysis orchestration with explicit abstention."""
import logging
from datetime import datetime, timezone
from uuid import uuid4
from app.schemas.analysis import AnalysisReport, ClaimAssessment, EvidenceReview, ResearchSource
from app.services.claim_extraction import extract_claim_candidates
from app.services.evidence_assessment import classify_review_rating
from app.services.evidence_provider import provider, EvidenceProviderError
from app.services.research_provider import research_provider, ResearchProviderError
from app.services.ml_service import get_prediction
from app.services.nli_provider import nli_provider, NLIProviderError

logger = logging.getLogger(__name__)

def analyze(text: str, source_type: str, preview: str) -> AnalysisReport:
    signal, score = "unavailable", None
    try:
        prediction = get_prediction(text)
        signal, score = prediction["model_signal"], prediction["confidence"]
    except Exception:
        logger.exception("Optional language-pattern classifier failed")

    claims, factcheck_available, research_available = [], True, True
    for candidate in extract_claim_candidates(text):
        try:
            raw_reviews = provider.search(candidate)
        except EvidenceProviderError:
            factcheck_available, raw_reviews = False, []
        reviews = []
        for item in raw_reviews:
            try:
                item["reviewer_stance"] = classify_review_rating(item.get("rating"))
                reviews.append(EvidenceReview(**item))
            except Exception:
                logger.warning("Skipping malformed fact-check provider review")

        try:
            raw_sources = research_provider.search(candidate)
        except ResearchProviderError:
            research_available, raw_sources = False, []
        sources = []
        for item in raw_sources:
            try:
                sources.append(ResearchSource(**item))
            except Exception:
                logger.warning("Skipping malformed research source")

        assessments = []
        # Assess only the highest-ranked search result to bound provider cost and latency.
        if sources:
            try:
                model_result = nli_provider.assess(candidate, sources[0].snippet)
                if model_result is not None:
                    assessments.append({
                        "source_url": sources[0].url,
                        **model_result,
                    })
            except NLIProviderError:
                assessments.append({
                    "source_url": sources[0].url,
                    "relation": "unavailable",
                    "score": None,
                    "model_id": "facebook/bart-large-mnli",
                })

        claims.append(ClaimAssessment(
            claim=candidate,
            status="existing_review_found" if reviews else "insufficient_evidence",
            explanation=(
                "A third-party fact-check review matched this candidate sentence. The stance shown is the review publisher's rating, not FactForge's independent finding. Check the review's date, context and cited evidence."
                if reviews else "No matching published fact-check review was found. Research links, if shown, are discovery leads and have not been independently assessed. No match is not proof of truth or falsity."
            ),
            matched_reviews=reviews,
            research_sources=sources,
            evidence_assessments=assessments,
        ))
    limitations = [
        "Sentence extraction produces candidate claims and may miss context, quotations, satire or compound claims.",
        "Fact-check search matches may be approximate; review ratings are attributed to their publishers and are not independently validated.",
        "The rating mapper is deliberately conservative and may abstain on unfamiliar rating vocabularies.",
        "Web search results are research leads. A government or education domain hint does not establish source authenticity, primacy or evidential support.",
        "The optional NLI model assesses only the top search snippet for each candidate; it does not authenticate the publisher, retrieve full primary evidence or independently establish factual truth.",
        "The ML classifier detects learned language patterns and does not determine factual truth.",
    ]
    if not factcheck_available:
        limitations.append("The fact-check provider was unavailable for at least one claim; review results are incomplete.")
    if not research_available:
        limitations.append("The web research provider was unavailable for at least one claim; source discovery is incomplete.")
    if not get_research_enabled():
        limitations.append("Tavily research search is not configured; add TAVILY_API_KEY to enable source discovery.")
    from app.core.config import get_settings
    if not get_settings().huggingface_api_token:
        limitations.append("The optional NLI assessment model is not configured; add HUGGINGFACE_API_TOKEN to assess top-ranked search snippets.")
    return AnalysisReport(
        analysis_id=str(uuid4()), created_at=datetime.now(timezone.utc),
        source_type=source_type, source_preview=preview,
        article_classifier_signal=signal, classifier_score=score,
        claims=claims,
        overall_status="evidence_found" if any(c.matched_reviews for c in claims) else "insufficient_evidence",
        limitations=limitations,
    )

def get_research_enabled() -> bool:
    from app.core.config import get_settings
    return bool(get_settings().tavily_api_key)
