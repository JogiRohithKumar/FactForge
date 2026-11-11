export interface EvidenceReview {
  publisher: string;
  title: string;
  url: string;
  rating: string | null;
  reviewer_stance: "reviewer_rates_claim_true" | "reviewer_rates_claim_false" | "reviewer_rates_claim_mixed" | "mixed_or_unclear";
  review_date: string | null;
  source: "google_fact_check";
}
export interface ResearchSource {
  title: string;
  url: string;
  snippet: string;
  relevance_score: number;
  source_classification: "potential_official_source" | "other_publisher";
}
export interface EvidenceAssessment {
  source_url: string;
  relation: "supports" | "contradicts" | "insufficient" | "uncertain" | "unavailable";
  score: number | null;
  model_id: string;
  disclaimer: string;
}
export interface ClaimAssessment {
  claim: string;
  status: "existing_review_found" | "insufficient_evidence";
  explanation: string;
  matched_reviews: EvidenceReview[];
  research_sources: ResearchSource[];
  evidence_assessments: EvidenceAssessment[];
}
export interface AnalysisReport {
  analysis_id: string;
  created_at: string;
  source_type: "text" | "url";
  source_preview: string;
  article_classifier_signal: "misleading_pattern" | "authentic_style_pattern" | "unavailable";
  classifier_score: number | null;
  classifier_disclaimer: string;
  claims: ClaimAssessment[];
  overall_status: "evidence_found" | "insufficient_evidence";
  limitations: string[];
}
export interface HistoryItem {
  id: string;
  is_fake: boolean;
  confidence: number;
  source_type: "text" | "url";
  source_preview: string;
  created_at: string;
}
export interface HistoryResponse { items: HistoryItem[]; }
export interface User { id: string; email: string; created_at: string; }
export interface AuthResponse { user: User; }
export interface ApiError { detail: string; }
