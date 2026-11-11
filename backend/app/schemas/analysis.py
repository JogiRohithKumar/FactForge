"""Public response contracts for evidence-led analysis."""
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field, HttpUrl

class EvidenceReview(BaseModel):
    publisher: str
    title: str
    url: HttpUrl
    rating: str | None = None
    reviewer_stance: Literal["reviewer_rates_claim_true", "reviewer_rates_claim_false", "reviewer_rates_claim_mixed", "mixed_or_unclear"]
    review_date: str | None = None
    source: Literal["google_fact_check"] = "google_fact_check"

class ResearchSource(BaseModel):
    title: str
    url: HttpUrl
    snippet: str
    relevance_score: float = Field(ge=0, le=1)
    source_classification: Literal["potential_official_source", "other_publisher"]

class EvidenceAssessment(BaseModel):
    source_url: HttpUrl
    relation: Literal["supports", "contradicts", "insufficient", "uncertain", "unavailable"]
    score: float | None = Field(default=None, ge=0, le=1)
    model_id: str
    disclaimer: str = "Experimental natural-language-inference signal over a search snippet; not a factual verdict."

class ClaimAssessment(BaseModel):
    claim: str
    status: Literal["existing_review_found", "insufficient_evidence"]
    explanation: str
    matched_reviews: list[EvidenceReview] = Field(default_factory=list)
    research_sources: list[ResearchSource] = Field(default_factory=list)
    evidence_assessments: list[EvidenceAssessment] = Field(default_factory=list)

class AnalysisReport(BaseModel):
    analysis_id: str
    created_at: datetime
    source_type: Literal["text", "url"]
    source_preview: str
    article_classifier_signal: Literal["misleading_pattern", "authentic_style_pattern", "unavailable"]
    classifier_score: float | None = Field(default=None, ge=0, le=100)
    classifier_disclaimer: str = "Language-pattern classification is not proof of factual accuracy."
    claims: list[ClaimAssessment]
    overall_status: Literal["evidence_found", "insufficient_evidence"]
    limitations: list[str]
