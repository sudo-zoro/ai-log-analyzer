import { useDatasets } from "../../hooks/useDatasets";
import { useModels } from "../../hooks/useModels";

function Dashboard() {
  const datasetsQuery = useDatasets();
  const modelsQuery = useModels();

  return (
    <section className="space-y-4">
      <div>
        <p className="text-xs uppercase tracking-[0.2em] text-cyan-300/80">Overview</p>
        <h1 className="text-3xl font-semibold text-white">Security Analytics Dashboard</h1>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <article className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
          <p className="text-sm text-slate-400">Datasets</p>
          <p className="mt-2 text-2xl font-semibold">{datasetsQuery.data?.length ?? 0}</p>
        </article>
        <article className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
          <p className="text-sm text-slate-400">Models</p>
          <p className="mt-2 text-2xl font-semibold">{modelsQuery.data?.length ?? 0}</p>
        </article>
        <article className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
          <p className="text-sm text-slate-400">Recent Detections</p>
          <p className="mt-2 text-2xl font-semibold">Soon</p>
        </article>
      </div>
    </section>
  );
}

export default Dashboard;
