import type { HistoryResponse, PredictionResult } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

class ApiRequestError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function handle<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail = `Request failed with status ${res.status}`;
    try {
      const body = await res.json();
      if (body?.detail) detail = body.detail;
    } catch {
      // response wasn't JSON; keep the generic message
    }
    throw new ApiRequestError(detail, res.status);
  }
  return res.json() as Promise<T>;
}

export async function analyzeText(text: string): Promise<PredictionResult> {
  const res = await fetch(`${API_BASE_URL}/predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  return handle<PredictionResult>(res);
}

export async function analyzeUrl(url: string): Promise<PredictionResult> {
  const res = await fetch(`${API_BASE_URL}/predict-url`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  });
  return handle<PredictionResult>(res);
}

export async function fetchHistory(limit = 20): Promise<HistoryResponse> {
  const res = await fetch(`${API_BASE_URL}/history?limit=${limit}`, {
    cache: "no-store",
  });
  return handle<HistoryResponse>(res);
}

export { ApiRequestError };
