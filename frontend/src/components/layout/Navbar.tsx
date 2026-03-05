function Navbar() {
  return (
    <header className="sticky top-0 z-10 flex h-16 items-center justify-between border-b border-slate-800/80 bg-slate-950/70 px-6 backdrop-blur">
      <div>
        <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Platform</p>
        <h2 className="text-lg font-semibold text-white">SecRAG AI</h2>
      </div>

      <div className="rounded-full border border-slate-700 bg-slate-900 px-3 py-1 text-xs text-slate-300">
        Security Analytics Dashboard
      </div>
    </header>
  );
}

export default Navbar;
