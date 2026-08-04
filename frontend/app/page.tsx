"use client";

import { useEffect, useState } from "react";
import { analyzeText, analyzeUrl, ApiRequestError, fetchHistory } from "@/lib/api";
import type { PredictionResult } from "@/lib/types";
import AnalyzerCard from "@/components/AnalyzerCard";
import ResultPanel from "@/components/ResultPanel";
import HistorySidebar from "@/components/HistorySidebar";
import Navbar from "@/components/Navbar";

export default function Home() {
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [history, setHistory] = useState<PredictionResult[]>([]);
  const [historyLoading, setHistoryLoading] = useState(true);

  const loadHistory = async () => {
    setHistoryLoading(true);
    try {
      const res = await fetchHistory();
      setHistory(res.items);
    } catch {
      // History is a nice-to-have sidebar; a failure here shouldn't block the main flow.
    } finally {
      setHistoryLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const runAnalysis = async (fn: () => Promise<PredictionResult>) => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await fn();
      setResult(res);
      loadHistory();
    } catch (e) {
      setResult(null);
      setError(e instanceof ApiRequestError ? e.message : "Unexpected error — please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-noise">
      <Navbar />
      <section className="mx-auto max-w-5xl px-6 py-14">
        <div className="max-w-2xl">
          <p className="font-mono text-xs uppercase tracking-[0.25em] text-amber-500">
            Exhibit A — submitted claim
          </p>
          <h1 className="mt-3 font-display text-4xl italic leading-tight text-paper sm:text-5xl">
            Every claim gets a case number.
          </h1>
          <p className="mt-4 text-paper-muted">
            Submit an article link or paste its text. FactForge runs it through a trained
            classifier and returns a verdict with a confidence report — logged for the record.
          </p>
        </div>

        <div className="mt-10 grid grid-cols-1 gap-8 lg:grid-cols-[minmax(0,1fr)_320px]">
          <div className="space-y-6">
            <AnalyzerCard
              onSubmitText={(text) => runAnalysis(() => analyzeText(text))}
              onSubmitUrl={(url) => runAnalysis(() => analyzeUrl(url))}
              isLoading={isLoading}
            />
            <ResultPanel result={result} error={error} />
          </div>
          <HistorySidebar items={history} isLoading={historyLoading} />
        </div>
      </section>
    </main>
  );
}
