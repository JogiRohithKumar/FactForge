import type { AnalysisReport, AuthResponse, HistoryResponse } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiRequestError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiRequestError";
    this.status = status;
  }
}

async function handle<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail = `Request failed with status ${res.status}`;
    try {
      const body = await res.json();
      if (body?.detail) detail = body.detail;
    } catch { /* retain the HTTP fallback */ }
    throw new ApiRequestError(detail, res.status);
  }
  return res.json() as Promise<T>;
}

async function post<T>(path: string, payload: object): Promise<T> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 60_000);
  try {
    const res = await fetch(`${API_BASE_URL}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify(payload),
      signal: controller.signal,
    });
    return await handle<T>(res);
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new ApiRequestError("The request timed out. Please try again.", 408);
    }
    throw error;
  } finally {
    clearTimeout(timeout);
  }
}

export function register(email: string, password: string): Promise<AuthResponse> {
  return post<AuthResponse>("/auth/register", { email, password });
}
export function login(email: string, password: string): Promise<AuthResponse> {
  return post<AuthResponse>("/auth/login", { email, password });
}
export function logout(): Promise<{ status: string }> {
  return post<{ status: string }>("/auth/logout", {});
}
export async function getCurrentUser(): Promise<AuthResponse> {
  const res = await fetch(`${API_BASE_URL}/auth/me`, { cache: "no-store", credentials: "include" });
  return handle<AuthResponse>(res);
}
export function analyzeText(text: string): Promise<AnalysisReport> {
  return post<AnalysisReport>("/api/v1/analyze/text", { text });
}
export function analyzeUrl(url: string): Promise<AnalysisReport> {
  return post<AnalysisReport>("/api/v1/analyze/url", { url });
}
export async function fetchHistory(limit = 20): Promise<HistoryResponse> {
  const res = await fetch(`${API_BASE_URL}/history?limit=${limit}`, { cache: "no-store", credentials: "include" });
  return handle<HistoryResponse>(res);
}
