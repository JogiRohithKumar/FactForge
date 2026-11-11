"use client";

import { useState, type FormEvent } from "react";
import { ApiRequestError, login, register } from "@/lib/api";
import type { User } from "@/lib/types";

interface AuthPanelProps { onAuthenticated: (user: User) => void; }

export default function AuthPanel({ onAuthenticated }: AuthPanelProps) {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const result = mode === "login" ? await login(email, password) : await register(email, password);
      onAuthenticated(result.user);
    } catch (err) {
      setError(err instanceof ApiRequestError ? err.message : "Unable to authenticate. Please try again.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <section className="case-file-border mx-auto mt-16 max-w-md rounded-xl bg-ink-900/70 p-7">
      <p className="font-mono text-xs uppercase tracking-[0.2em] text-amber-400">Private research workspace</p>
      <h1 className="mt-3 font-display text-3xl italic text-paper">{mode === "login" ? "Welcome back." : "Create your account."}</h1>
      <p className="mt-2 text-sm text-paper-muted">Your analysis history is private to your account.</p>
      <form onSubmit={submit} className="mt-6 space-y-4">
        <label className="block text-xs font-mono uppercase tracking-widest text-paper-faint">
          Email
          <input type="email" autoComplete="email" required value={email} onChange={e => setEmail(e.target.value)} className="mt-2 w-full rounded-lg border border-ink-600 bg-ink-950 px-3 py-3 text-sm normal-case tracking-normal text-paper" />
        </label>
        <label className="block text-xs font-mono uppercase tracking-widest text-paper-faint">
          Password
          <input type="password" autoComplete={mode === "login" ? "current-password" : "new-password"} minLength={12} maxLength={128} required value={password} onChange={e => setPassword(e.target.value)} className="mt-2 w-full rounded-lg border border-ink-600 bg-ink-950 px-3 py-3 text-sm normal-case tracking-normal text-paper" />
          <span className="mt-1 block text-[11px] normal-case tracking-normal">Use at least 12 characters.</span>
        </label>
        {error && <p role="alert" className="text-sm text-flagged">{error}</p>}
        <button disabled={busy} className="w-full rounded-lg bg-amber-500 px-4 py-3 font-mono text-sm font-semibold uppercase tracking-widest text-ink-950 disabled:opacity-50">
          {busy ? "Please wait…" : mode === "login" ? "Sign in" : "Create account"}
        </button>
      </form>
      <button type="button" onClick={() => { setMode(mode === "login" ? "register" : "login"); setError(null); }} className="mt-5 w-full text-sm text-paper-muted hover:text-amber-400">
        {mode === "login" ? "New to FactForge? Create an account" : "Already registered? Sign in"}
      </button>
    </section>
  );
}
