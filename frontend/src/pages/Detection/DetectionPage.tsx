import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { useRunDetection } from "../../hooks/useDetection";
import { useModels } from "../../hooks/useModels";
import type { DetectionRun } from "../../types/detection";

type DetectionPageProps = {
  selectedDetection: DetectionRun | null;
  onDetectionComplete: (result: DetectionRun) => void;
};

function DetectionPage({ selectedDetection, onDetectionComplete }: DetectionPageProps) {
  const navigate = useNavigate();
  const modelsQuery = useModels();
  const detectionMutation = useRunDetection();

  const readyModels = useMemo(
    () => (modelsQuery.data ?? []).filter((model) => model.status === "ready"),
    [modelsQuery.data],
  );

  const [modelId, setModelId] = useState("");
  const [file, setFile] = useState<File | null>(null);

  const detectionError = useMemo(() => {
    if (!detectionMutation.error) {
      return "";
    }
    if (axios.isAxiosError(detectionMutation.error)) {
      return (detectionMutation.error.response?.data as { detail?: string } | undefined)?.detail ?? detectionMutation.error.message;
    }
    return "Detection failed.";
  }, [detectionMutation.error]);

  const run = selectedDetection ?? detectionMutation.data ?? null;
  const anomalies = run?.results?.anomalies ?? [];

  const onSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!modelId || !file) {
      return;
    }

    detectionMutation.mutate(
      { model_id: modelId, file },
      {
        onSuccess: (result) => {
          onDetectionComplete(result);
          event.currentTarget.reset();
          setFile(null);
        },
      },
    );
  };

  return (
    <section className="space-y-6">
      <header>
        <p className="text-xs uppercase tracking-[0.2em] text-amber-300/80">Detection</p>
        <h1 className="text-3xl font-semibold text-white">Run Anomaly Detection</h1>
      </header>

      <div className="grid gap-6 lg:grid-cols-[1fr_1.8fr]">
        <article className="rounded-xl border border-slate-800 bg-slate-900/60 p-5">
          <h2 className="text-lg font-semibold text-slate-100">New Detection Run</h2>
          <p className="mt-1 text-sm text-slate-400">Select a trained model and upload log CSV.</p>

          <form className="mt-4 space-y-4" onSubmit={onSubmit}>
            <label className="block space-y-1">
              <span className="text-sm text-slate-300">Model</span>
              <select
                className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none ring-amber-400 transition focus:ring"
                value={modelId}
                onChange={(event) => setModelId(event.target.value)}
                required
              >
                <option value="">Select ready model</option>
                {readyModels.map((model) => (
                  <option key={model.id} value={model.id}>
                    {model.name}
                  </option>
                ))}
              </select>
            </label>

            <label className="block space-y-1">
              <span className="text-sm text-slate-300">CSV File</span>
              <input
                className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-300 file:mr-3 file:rounded-md file:border-0 file:bg-amber-500/20 file:px-3 file:py-2 file:text-amber-300"
                type="file"
                accept=".csv"
                onChange={(event) => setFile(event.target.files?.[0] ?? null)}
                required
              />
            </label>

            {detectionError ? <p className="text-sm text-rose-400">{detectionError}</p> : null}

            <button
              className="rounded-lg bg-amber-400 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-amber-300 disabled:cursor-not-allowed disabled:bg-slate-700 disabled:text-slate-400"
              type="submit"
              disabled={detectionMutation.isPending || readyModels.length === 0}
            >
              {detectionMutation.isPending ? "Running..." : "Run Detection"}
            </button>
          </form>
        </article>

        <article className="rounded-xl border border-slate-800 bg-slate-900/60 p-5">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-slate-100">Detection Output</h2>
            <button
              className="rounded-md border border-cyan-500/40 px-3 py-1 text-xs text-cyan-300 hover:bg-cyan-500/10 disabled:cursor-not-allowed disabled:opacity-50"
              type="button"
              onClick={() => navigate("/insights")}
              disabled={anomalies.length === 0}
            >
              Send To AI Insights
            </button>
          </div>

          {run ? (
            <div className="space-y-4">
              <div className="grid gap-3 sm:grid-cols-3">
                <div className="rounded-lg border border-slate-800 bg-slate-950/70 p-3">
                  <p className="text-xs text-slate-400">Total Rows</p>
                  <p className="mt-1 text-xl font-semibold">{run.total_rows ?? 0}</p>
                </div>
                <div className="rounded-lg border border-slate-800 bg-slate-950/70 p-3">
                  <p className="text-xs text-slate-400">Anomalies</p>
                  <p className="mt-1 text-xl font-semibold text-amber-300">{run.anomaly_count ?? 0}</p>
                </div>
                <div className="rounded-lg border border-slate-800 bg-slate-950/70 p-3">
                  <p className="text-xs text-slate-400">Anomaly Ratio</p>
                  <p className="mt-1 text-xl font-semibold">{((run.anomaly_ratio ?? 0) * 100).toFixed(2)}%</p>
                </div>
              </div>

              <div className="overflow-x-auto">
                <table className="min-w-full text-left text-sm">
                  <thead className="text-xs uppercase tracking-wide text-slate-400">
                    <tr className="border-b border-slate-800">
                      <th className="px-2 py-2">Row</th>
                      <th className="px-2 py-2">Score</th>
                      <th className="px-2 py-2">Raw Data</th>
                    </tr>
                  </thead>
                  <tbody>
                    {anomalies.map((anomaly) => (
                      <tr className="border-b border-slate-800/80 text-slate-200" key={`${anomaly.row_index}-${anomaly.score}`}>
                        <td className="px-2 py-3">{anomaly.row_index}</td>
                        <td className="px-2 py-3">{anomaly.score.toFixed(4)}</td>
                        <td className="px-2 py-3 text-xs text-slate-300">{JSON.stringify(anomaly.raw_row)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>

                {anomalies.length === 0 ? <p className="py-6 text-center text-sm text-slate-400">No anomalies returned.</p> : null}
              </div>
            </div>
          ) : (
            <p className="text-slate-400">Run a detection to see anomaly details.</p>
          )}
        </article>
      </div>
    </section>
  );
}

export default DetectionPage;
