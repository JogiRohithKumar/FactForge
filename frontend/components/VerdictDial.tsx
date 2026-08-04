"use client";

import type { CSSProperties } from "react";

interface VerdictDialProps {
  confidence: number; // 0-100
  isFake: boolean;
}

const SIZE = 168;
const STROKE = 10;
const RADIUS = (SIZE - STROKE) / 2;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;

export default function VerdictDial({ confidence, isFake }: VerdictDialProps) {
  const pct = Math.max(0, Math.min(100, confidence)) / 100;
  const dashTarget = CIRCUMFERENCE * (1 - pct);
  const accent = isFake ? "#F2545B" : "#3DDC97";

  return (
    <div className="relative inline-flex items-center justify-center">
      <svg width={SIZE} height={SIZE} viewBox={`0 0 ${SIZE} ${SIZE}`} className="-rotate-90">
        <circle
          cx={SIZE / 2}
          cy={SIZE / 2}
          r={RADIUS}
          fill="none"
          stroke="#1C2740"
          strokeWidth={STROKE}
        />
        <circle
          cx={SIZE / 2}
          cy={SIZE / 2}
          r={RADIUS}
          fill="none"
          stroke={accent}
          strokeWidth={STROKE}
          strokeLinecap="round"
          strokeDasharray={CIRCUMFERENCE}
          strokeDashoffset={dashTarget}
          className="animate-dash-in"
          style={
            {
              "--dash-full": CIRCUMFERENCE,
              "--dash-target": dashTarget,
            } as CSSProperties
          }
        />
      </svg>
      <div className="absolute flex flex-col items-center">
        <span className="font-mono text-3xl font-medium text-paper">
          {confidence.toFixed(1)}
          <span className="text-lg text-paper-muted">%</span>
        </span>
        <span className="mt-1 text-[11px] uppercase tracking-[0.2em] text-paper-muted">
          confidence
        </span>
      </div>
      <div
        className="absolute -right-3 -top-3 rotate-[12deg] rounded-sm border-2 px-2 py-0.5 text-[10px] font-bold uppercase tracking-widest"
        style={{ borderColor: accent, color: accent }}
      >
        {isFake ? "Flagged" : "Verified"}
      </div>
    </div>
  );
}
