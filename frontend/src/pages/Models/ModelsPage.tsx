import { useMemo, useState } from "react";
import axios from "axios";
import { useDatasets } from "../../hooks/useDatasets";
import { useDeleteModel, useModels, useTrainModel } from "../../hooks/useModels";
import { formatDateTime } from "../../utils/format";

function ModelsPage() {
  const datasetsQuery = useDatasets();
  const modelsQuery = useModels();
  const trainMutation = useTrainModel();
  const deleteMutation = useDeleteModel();

  const [form, setForm] = useState({
    datasetId: "",
    modelName: "",
    nEstimators: 100,
    contamination: 0.05,
  });

  const trainingError = useMemo(() => {
    if (!trainMutation.error) {
      return "";
    }
    if (axios.isAxiosError(trainMutation.error)) {
      return (trainMutation.error.response?.data as { detail?: string } | undefined)?.detail ?? trainMutation.error.message;
    }
    return "Training failed.";
  }, [trainMutation.error]);

  const onSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!form.datasetId || !form.modelName.trim()) {
      return;
    }

    trainMutation.mutate(
      {
        dataset_id: form.datasetId,
        model_name: form.modelName.trim(),
        n_estimators: form.nEstimators,
        contamination: form.contamination,
      },
      {
        onSuccess: () => {
          setForm((prev) => ({ ...prev, modelName: "" }));
        },
      },
    );
  };

  return (
    <section className="space-y-6">
      <header>
        <p className="text-xs uppercase tracking-[0.2em] text-emerald-300/80">Models</p>
        <h1 className="text-3xl font-semibold text-white">Train and Manage Anomaly Models</h1>
      </header>

      <div className="grid gap-6 lg:grid-cols-[1fr_1.7fr]">
        <article className="rounded-xl border border-slate-800 bg-slate-900/60 p-5">
          <h2 className="text-lg font-semibold text-slate-100">Train Isolation Forest</h2>
          <p className="mt-1 text-sm text-slate-400">Choose a dataset and model hyperparameters.</p>

          <form className="mt-4 space-y-4" onSubmit={onSubmit}>
            <label className="block space-y-1">
              <span className="text-sm text-slate-300">Dataset</span>
              <select
                className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none ring-emerald-400 transition focus:ring"
                value={form.datasetId}
                onChange={(event) => setForm((prev) => ({ ...prev, datasetId: event.target.value }))}
                required
              >
                <option value="">Select dataset</option>
                {(datasetsQuery.data ?? []).map((dataset) => (
                  <option key={dataset.id} value={dataset.id}>
                    {dataset.name}
                  </option>
                ))}
              </select>
            </label>

            <label className="block space-y-1">
              <span className="text-sm text-slate-300">Model Name</span>
              <input
                className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none ring-emerald-400 transition focus:ring"
                placeholder="Isolation Forest - Auth"
                value={form.modelName}
                onChange={(event) => setForm((prev) => ({ ...prev, modelName: event.target.value }))}
                required
              />
            </label>

            <div className="grid grid-cols-2 gap-3">
              <label className="space-y-1">
                <span className="text-sm text-slate-300">n_estimators</span>
                <input
                  className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none ring-emerald-400 transition focus:ring"
                  type="number"
                  min={10}
                  max={1000}
                  value={form.nEstimators}
                  onChange={(event) => setForm((prev) => ({ ...prev, nEstimators: Number(event.target.value) }))}
                  required
                />
              </label>

              <label className="space-y-1">
                <span className="text-sm text-slate-300">contamination</span>
                <input
                  className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none ring-emerald-400 transition focus:ring"
                  type="number"
                  min={0.001}
                  max={0.5}
                  step={0.001}
                  value={form.contamination}
                  onChange={(event) => setForm((prev) => ({ ...prev, contamination: Number(event.target.value) }))}
                  required
                />
              </label>
            </div>

            {trainingError ? <p className="text-sm text-rose-400">{trainingError}</p> : null}

            <button
              className="rounded-lg bg-emerald-500 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-emerald-400 disabled:cursor-not-allowed disabled:bg-slate-700 disabled:text-slate-400"
              type="submit"
              disabled={trainMutation.isPending || datasetsQuery.isLoading || (datasetsQuery.data?.length ?? 0) === 0}
            >
              {trainMutation.isPending ? "Training..." : "Train Model"}
            </button>
          </form>
        </article>

        <article className="rounded-xl border border-slate-800 bg-slate-900/60 p-5">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-slate-100">Model Registry</h2>
            <span className="rounded-full border border-slate-700 px-3 py-1 text-xs text-slate-300">
              {modelsQuery.data?.length ?? 0} total
            </span>
          </div>

          {modelsQuery.isLoading ? <p className="text-slate-400">Loading models...</p> : null}
          {modelsQuery.isError ? <p className="text-rose-400">Failed to load models.</p> : null}

          {!modelsQuery.isLoading && !modelsQuery.isError ? (
            <div className="overflow-x-auto">
              <table className="min-w-full text-left text-sm">
                <thead className="text-xs uppercase tracking-wide text-slate-400">
                  <tr className="border-b border-slate-800">
                    <th className="px-2 py-2">Name</th>
                    <th className="px-2 py-2">Algorithm</th>
                    <th className="px-2 py-2">Status</th>
                    <th className="px-2 py-2">Dataset</th>
                    <th className="px-2 py-2">Created</th>
                    <th className="px-2 py-2">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {(modelsQuery.data ?? []).map((model) => (
                    <tr className="border-b border-slate-800/80 text-slate-200" key={model.id}>
                      <td className="px-2 py-3">
                        <p className="font-medium">{model.name}</p>
                        <p className="text-xs text-slate-400">{model.id.slice(0, 8)}</p>
                      </td>
                      <td className="px-2 py-3">{model.algorithm}</td>
                      <td className="px-2 py-3">
                        <span
                          className={[
                            "rounded-full px-2 py-1 text-xs",
                            model.status === "ready"
                              ? "bg-emerald-500/20 text-emerald-300"
                              : model.status === "error"
                                ? "bg-rose-500/20 text-rose-300"
                                : "bg-amber-500/20 text-amber-300",
                          ].join(" ")}
                        >
                          {model.status}
                        </span>
                      </td>
                      <td className="px-2 py-3">{model.dataset_id ? model.dataset_id.slice(0, 8) : "-"}</td>
                      <td className="px-2 py-3">{formatDateTime(model.created_at)}</td>
                      <td className="px-2 py-3">
                        <button
                          className="rounded-md border border-rose-500/40 px-3 py-1 text-xs text-rose-300 hover:bg-rose-500/10 disabled:cursor-not-allowed disabled:opacity-50"
                          onClick={() => deleteMutation.mutate(model.id)}
                          disabled={deleteMutation.isPending}
                          type="button"
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>

              {(modelsQuery.data ?? []).length === 0 ? (
                <p className="py-6 text-center text-sm text-slate-400">No models trained yet.</p>
              ) : null}
            </div>
          ) : null}
        </article>
      </div>
    </section>
  );
}

export default ModelsPage;
