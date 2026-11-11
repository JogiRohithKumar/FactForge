"use client";

import type { AnalysisReport } from "@/lib/types";

interface ResultPanelProps { result: AnalysisReport | null; error: string | null; }

export default function ResultPanel({ result, error }: ResultPanelProps) {
  if (error) return (
    <div className="case-file-border rounded-xl border-flagged/40 bg-flagged/5 p-6">
      <p className="font-mono text-xs uppercase tracking-widest text-flagged">Analysis could not be completed</p>
      <p className="mt-2 text-sm text-paper-muted">{error}</p>
    </div>
  );

  if (!result) return (
    <div className="case-file-border flex min-h-[220px] flex-col items-center justify-center rounded-xl border-dashed p-6 text-center">
      <p className="font-display text-lg italic text-paper-muted">No analysis open yet</p>
      <p className="mt-2 max-w-xs text-sm text-paper-faint">Submit a link or text to inspect candidate claims and discover related fact-check reviews.</p>
    </div>
  );

  return (
    <section className="case-file-border space-y-5 rounded-xl bg-ink-900/60 p-6">
      <div>
        <p className="font-mono text-[11px] uppercase tracking-[0.2em] text-paper-faint">Analysis #{result.analysis_id.slice(0, 8)}</p>
        <h2 className="mt-2 text-lg text-paper">
          {result.overall_status === "evidence_found" ? "Existing fact-check reviews found" : "No matching fact-check review found"}
        </h2>
        <p className="mt-2 text-sm text-paper-muted">{result.classifier_disclaimer}</p>
      </div>

      <div className="rounded-lg border border-ink-700 p-4">
        <p className="font-mono text-[11px] uppercase tracking-widest text-paper-faint">Language-pattern signal</p>
        <p className="mt-2 text-sm text-paper">
          {result.article_classifier_signal === "misleading_pattern" ? "Patterns associated with the model's misleading-text training examples" :
           result.article_classifier_signal === "authentic_style_pattern" ? "Patterns associated with the model's authentic-style training examples" :
           "Classifier unavailable"}
        </p>
        {result.classifier_score !== null && <p className="mt-1 text-xs text-paper-faint">Model score: {result.classifier_score.toFixed(1)}% (not a probability that the article is true or false)</p>}
      </div>

      <div className="space-y-4">
        <h3 className="font-mono text-xs uppercase tracking-widest text-paper-faint">Candidate claims ({result.claims.length})</h3>
        {result.claims.length === 0 && <p className="text-sm text-paper-muted">No sentence-length claim candidates could be extracted from this material.</p>}
        {result.claims.map((item, index) => (
          <article key={index} className="rounded-lg border border-ink-700/80 p-4">
            <p className="text-sm leading-relaxed text-paper">{item.claim}</p>
            <p className="mt-3 text-xs leading-relaxed text-paper-muted">{item.explanation}</p>
            {item.research_sources.length > 0 && (
              <div className="mt-3 space-y-2">
                <p className="font-mono text-[10px] uppercase tracking-widest text-paper-faint">Research leads — independently inspect before relying on them</p>
                {item.research_sources.map((source, sourceIndex) => (
                  <a key={sourceIndex} href={source.url} target="_blank" rel="noreferrer" className="block rounded-md border border-ink-700 bg-ink-950/50 p-3 hover:bg-ink-800">
                    <span className="block text-xs font-semibold text-paper">{source.title}</span>
                    <span className="mt-1 block text-xs text-paper-muted">{source.snippet}</span>
                    <span className="mt-2 block text-[10px] uppercase tracking-wider text-amber-400">{source.source_classification.replaceAll("_", " ")} · relevance {Math.round(source.relevance_score * 100)}%</span>
                  </a>
                ))}
              </div>
            )}
            {item.evidence_assessments.length > 0 && (
              <div className="mt-3 rounded-md border border-amber-500/20 bg-amber-500/5 p-3">
                <p className="font-mono text-[10px] uppercase tracking-widest text-amber-400">Experimental NLI signal — not a verdict</p>
                {item.evidence_assessments.map((assessment, assessmentIndex) => (
                  <div key={assessmentIndex} className="mt-2">
                    <p className="text-xs text-paper">Model relation: <span className="font-semibold">{assessment.relation}</span></p>
                    {assessment.score !== null && <p className="mt-1 text-[11px] text-paper-faint">Uncalibrated model score: {(assessment.score * 100).toFixed(1)}%</p>}
                    <p className="mt-1 break-all text-[10px] text-paper-faint">{assessment.model_id}</p>
                    <a href={assessment.source_url} target="_blank" rel="noreferrer" className="mt-1 block text-[11px] text-amber-400 underline">Inspect assessed source</a>
                    <p className="mt-1 text-[10px] leading-relaxed text-paper-faint">{assessment.disclaimer}</p>
                  </div>
                ))}
              </div>
            )}
            {item.matched_reviews.length > 0 && (
              <div className="mt-3 space-y-2">
                {item.matched_reviews.map((review, reviewIndex) => (
                  <a key={reviewIndex} href={review.url} target="_blank" rel="noreferrer" className="block rounded-md bg-ink-800 p-3 hover:bg-ink-700">
                    <span className="block text-xs font-semibold text-amber-400">{review.publisher}</span>
                    <span className="mt-1 block text-sm text-paper">{review.title}</span>
                    {review.rating && <span className="mt-1 block text-xs text-paper-muted">Published rating: {review.rating}</span>}
                    <span className="mt-1 block text-xs text-paper-faint">Publisher stance: {review.reviewer_stance.replaceAll("_", " ")}</span>
                    {review.review_date && <span className="mt-1 block text-xs text-paper-faint">Review date: {review.review_date}</span>}
                  </a>
                ))}
              </div>
            )}
          </article>
        ))}
      </div>

      <div className="rounded-lg border border-amber-500/30 bg-amber-500/5 p-4">
        <h3 className="font-mono text-xs uppercase tracking-widest text-amber-400">Limitations</h3>
        <ul className="mt-2 list-disc space-y-1 pl-5 text-xs leading-relaxed text-paper-muted">
          {result.limitations.map((limitation, index) => <li key={index}>{limitation}</li>)}
        </ul>
      </div>
    </section>
  );
}
