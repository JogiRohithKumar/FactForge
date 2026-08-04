export default function Navbar() {
  return (
    <header className="border-b border-ink-700/80">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-5">
        <div className="flex items-baseline gap-2">
          <span className="font-display text-xl italic tracking-tight text-paper">
            FactForge
          </span>
          <span className="hidden font-mono text-[11px] uppercase tracking-[0.25em] text-paper-faint sm:inline">
            Case File System
          </span>
        </div>
        <a
          href="https://github.com"
          className="font-mono text-xs uppercase tracking-widest text-paper-muted transition hover:text-amber-400"
        >
          Docs
        </a>
      </div>
    </header>
  );
}
