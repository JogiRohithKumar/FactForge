"use client";

import { useEffect, useState } from "react";
import { analyzeText, analyzeUrl, ApiRequestError, fetchHistory, getCurrentUser, logout } from "@/lib/api";
import type { AnalysisReport, HistoryItem, User } from "@/lib/types";
import AnalyzerCard from "@/components/AnalyzerCard";
import ResultPanel from "@/components/ResultPanel";
import HistorySidebar from "@/components/HistorySidebar";
import Navbar from "@/components/Navbar";
import AuthPanel from "@/components/AuthPanel";

export default function Home() {
  const [user, setUser] = useState<User | null>(null);
  const [authLoading, setAuthLoading] = useState(true);
  const [result, setResult] = useState<AnalysisReport | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [historyLoading, setHistoryLoading] = useState(false);

  const loadHistory = async () => {
    setHistoryLoading(true);
    try {
      const res = await fetchHistory();
      setHistory(res.items);
    } catch {
      setHistory([]);
    } finally {
      setHistoryLoading(false);
    }
  };

  useEffect(() => {
    getCurrentUser()
      .then(({ user: current }) => { setUser(current); })
      .catch(() => { setUser(null); })
      .finally(() => setAuthLoading(false));
  }, []);

  useEffect(() => {
    if (user) void loadHistory();
  }, [user]);

  const runAnalysis = async (fn: () => Promise<AnalysisReport>) => {
    setIsLoading(true);
    setError(null);
    try {
      const report = await fn();
      setResult(report);
      void loadHistory();
    } catch (e) {
      setResult(null);
      setError(e instanceof ApiRequestError ? e.message : "Unexpected error — please try again.");
      if (e instanceof ApiRequestError && e.status === 401) setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  const signOut = async () => {
    try { await logout(); } finally {
      setUser(null);
      setResult(null);
      setHistory([]);
    }
  };

  return (
    <main className="min-h-screen bg-noise">
      <Navbar />
      {authLoading ? (
        <p className="py-20 text-center font-mono text-sm text-paper-muted">Checking secure session…</p>
      ) : !user ? (
        <AuthPanel onAuthenticated={setUser} />
      ) : (
        <section className="mx-auto max-w-5xl px-6 py-10">
          <div className="mb-8 flex flex-wrap items-center justify-between gap-3 border-b border-ink-700 pb-4">
            <div>
              <p className="font-mono text-[11px] uppercase tracking-widest text-paper-faint">Signed in</p>
              <p className="mt-1 text-sm text-paper">{user.email}</p>
            </div>
            <button onClick={() => void signOut()} className="rounded-md border border-ink-600 px-3 py-2 text-xs font-mono uppercase tracking-widest text-paper-muted hover:text-paper">Sign out</button>
          </div>
          <div className="max-w-2xl">
            <p className="font-mono text-xs uppercase tracking-[0.25em] text-amber-500">Evidence desk — submitted material</p>
            <h1 className="mt-3 font-display text-4xl italic leading-tight text-paper sm:text-5xl">Every claim deserves evidence.</h1>
            <p className="mt-4 text-paper-muted">
              Submit an article link or paste text. FactForge identifies candidate claims,
              searches for existing fact-check reviews, and clearly separates evidence from
              language-pattern signals. A missing review is never treated as proof of truth.
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
      )}
    </main>
  );
}
