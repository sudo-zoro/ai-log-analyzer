import { NavLink } from "react-router-dom";

const navItems = [
  { label: "Dashboard", to: "/" },
  { label: "Datasets", to: "/datasets" },
  { label: "Models", to: "/models" },
  { label: "Detection", to: "/detection" },
  { label: "AI Insights", to: "/insights" },
];

function Sidebar() {
  return (
   <aside className="flex h-screen w-64 flex-col border-r border-slate-800/80 bg-slate-950/80 backdrop-blur">

      <div className="border-b border-slate-800/80 px-6 py-5">
        <p className="text-xs uppercase tracking-[0.22em] text-cyan-400/80">SecRAG Console</p>
        <h1 className="mt-1 text-xl font-semibold text-slate-100">Security Ops</h1>
      </div>

      <nav className="flex-1 space-y-1 px-3 py-4">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              [
                "block rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-slate-800 text-cyan-300"
                  : "text-slate-300 hover:bg-slate-800/70 hover:text-slate-100",
              ].join(" ")
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>

     <div className="mt-auto border-t border-slate-800/80 px-4 py-4 text-xs text-slate-500">v0.1.0</div>

    </aside>
  );
}

export default Sidebar;
