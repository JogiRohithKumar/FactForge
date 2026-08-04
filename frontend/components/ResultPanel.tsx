"use client";

import type { PredictionResult } from "@/lib/types";
import VerdictDial from "./VerdictDial";

interface ResultPanelProps {
  result: PredictionResult | null;
  error: string | null;
}

export default function ResultPanel({ result, error }: ResultPanelProps) {
  if (error) {
    return (
      <div className="case-file-border rounded-xl border-flagged/40 bg-flagged/5 p-6">
        <p className="font-mono text-xs uppercase tracking-widest text-flagged">
          Case could not be opened
        </p>
        <p className="mt-2 text-sm text-paper-muted">{error}</p>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="case-file-border flex h-full min-h-[220px] flex-col items-center justify-center rounded-xl border-dashed p-6 text-center">
        <p className="font-display text-lg italic text-paper-muted">No case open yet</p>
        <p className="mt-2 max-w-xs text-sm text-paper-faint">
          Submit a link or paste an article to generate a verdict and confidence report.
        </p>
      </div>
    );
  }

  return (
    <div className="case-file-border animate-in rounded-xl bg-ink-900/60 p-6">
      <p className="font-mono text-[11px] uppercase tracking-[0.2em] text-paper-faint">
        Report #{result.id.slice(0, 8)}
      </p>
      <div className="mt-4 flex flex-col items-center gap-4 sm:flex-row sm:items-start sm:justify-between">
        <VerdictDial confidence={result.confidence} isFake={result.is_fake} />
        <div className="flex-1 space-y-2 text-sm">
          <p className="text-paper-muted">
            Source ({result.source_type}):{" "}
            <span className="font-mono text-paper">{result.source_preview}</span>
          </p>
          <p className="text-paper-muted">
            {result.is_fake
              ? "The language pattern matches profiles the model associates with fabricated or misleading reporting."
              : "The language pattern is consistent with the model's authentic-reporting profile."}
          </p>
        </div>
      </div>
    </div>
  );
}
