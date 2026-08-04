"use client";

import { useState, type FormEvent } from "react";

interface AnalyzerCardProps {
  onSubmitText: (text: string) => void;
  onSubmitUrl: (url: string) => void;
  isLoading: boolean;
}

type Mode = "text" | "url";

export default function AnalyzerCard({ onSubmitText, onSubmitUrl, isLoading }: AnalyzerCardProps) {
  const [mode, setMode] = useState<Mode>("url");
  const [text, setText] = useState("");
  const [url, setUrl] = useState("");

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (mode === "text" && text.trim().length >= 20) onSubmitText(text.trim());
    if (mode === "url" && url.trim().length > 0) onSubmitUrl(url.trim());
  };

  const textTooShort = mode === "text" && text.length > 0 && text.trim().length < 20;

  return (
    <div className="case-file-border rounded-xl bg-ink-900/60 p-1 shadow-2xl shadow-black/30">
      <div className="flex gap-1 p-2">
        {(["url", "text"] as Mode[]).map((m) => (
          <button
            key={m}
            type="button"
            onClick={() => setMode(m)}
            className={`rounded-md px-4 py-2 font-mono text-xs uppercase tracking-widest transition ${
              mode === m
                ? "bg-ink-700 text-amber-400"
                : "text-paper-muted hover:text-paper"
            }`}
          >
            {m === "url" ? "Submit link" : "Paste text"}
          </button>
        ))}
      </div>

      <form onSubmit={handleSubmit} className="space-y-3 p-5 pt-2">
        {mode === "url" ? (
          <input
            type="url"
            required
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://www.example.com/article-headline"
            className="w-full rounded-lg border border-ink-600 bg-ink-950/60 px-4 py-3 font-mono text-sm text-paper placeholder:text-paper-faint focus:border-amber-500"
          />
        ) : (
          <textarea
            required
            rows={7}
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Paste the article body here (minimum 20 characters)..."
            className="w-full resize-none rounded-lg border border-ink-600 bg-ink-950/60 px-4 py-3 text-sm text-paper placeholder:text-paper-faint focus:border-amber-500"
          />
        )}
        {textTooShort && (
          <p className="font-mono text-xs text-flagged">Needs at least 20 characters.</p>
        )}

        <button
          type="submit"
          disabled={isLoading}
          className="w-full rounded-lg bg-gradient-to-r from-amber-600 to-amber-500 px-4 py-3 font-mono text-sm font-semibold uppercase tracking-widest text-ink-950 transition hover:from-amber-500 hover:to-amber-400 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isLoading ? "Analyzing…" : "Open case"}
        </button>
      </form>
    </div>
  );
}
