export interface PredictionResult {
  id: string;
  is_fake: boolean;
  confidence: number;
  source_type: "text" | "url";
  source_preview: string;
  created_at: string;
}

export interface HistoryResponse {
  items: PredictionResult[];
}

export interface ApiError {
  detail: string;
}
