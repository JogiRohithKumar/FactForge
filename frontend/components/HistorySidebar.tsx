"use client";

import type { PredictionResult } from "@/lib/types";

interface HistorySidebarProps {
  items: PredictionResult[];
  isLoading: boolean;
}

export default function HistorySidebar({ items, isLoading }: HistorySidebarProps) {
  return (
    <aside className="case-file-border rounded-xl bg-ink-900/40 p-5">
      <p className="font-mono text-xs uppercase tracking-[0.2em] text-paper-faint">Case log</p>
      <div className="mt-4 space-y-3">
        {isLoading && <p className="text-sm text-paper-faint">Loading…</p>}
        {!isLoading && items.length === 0 && (
          <p className="text-sm text-paper-faint">No prior cases this session.</p>
        )}
        {items.map((item) => (
          <div
            key={item.id}
            className="flex items-center justify-between border-b border-ink-700/60 pb-2 last:border-none"
          >
            <div className="min-w-0">
              <p className="truncate font-mono text-xs text-paper">{item.source_preview}</p>
              <p className="text-[11px] text-paper-faint">
                {new Date(item.created_at).toLocaleString()}
              </p>
            </div>
            <span
              className={`ml-3 shrink-0 rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide ${
                item.is_fake ? "bg-flagged/15 text-flagged" : "bg-verified/15 text-verified"
              }`}
            >
              {item.is_fake ? "Flagged" : "Verified"}
            </span>
          </div>
        ))}
      </div>
    </aside>
  );
}
