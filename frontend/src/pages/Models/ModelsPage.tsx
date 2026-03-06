import { useMemo, useState } from "react";
import axios from "axios";
import { useDatasets } from "../../hooks/useDatasets";
import { useDeleteModel, useModels, useTrainModel } from "../../hooks/useModels";
import type { ModelAlgorithm } from "../../types/model";
import { formatDateTime } from "../../utils/format";

function formatAlgorithmLabel(algorithm: string): string {
  if (algorithm === "isolation_forest") {
    return "Isolation Forest";
  }
  if (algorithm === "one_class_svm") {
    return "One-Class SVM";
  }
  if (algorithm === "autoencoder") {
    return "Autoencoder";
  }
  return algorithm;
}

function previewHyperparameters(params: Record<string, unknown> | null): string {
  if (!params) {
    return "-";
  }
  return Object.entries(params)
    .slice(0, 3)
    .map(([key, value]) => `${key}=${String(value)}`)
    .join(" • ");
}

function ModelsPage() {
  const datasetsQuery = useDatasets();
  const modelsQuery = useModels();
  const trainMutation = useTrainModel();
  const deleteMutation = useDeleteModel();

  const [datasetId, setDatasetId] = useState("");
  const [modelName, setModelName] = useState("");
  const [algorithm, setAlgorithm] = useState<ModelAlgorithm>("isolation_forest");

  const [nEstimators, setNEstimators] = useState(100);
  const [contamination, setContamination] = useState(0.05);

  const [kernel, setKernel] = useState("rbf");
  const [nu, setNu] = useState(0.05);
  const [gamma, setGamma] = useState("scale");
  const [hiddenDim, setHiddenDim] = useState(16);
  const [epochs, setEpochs] = useState(80);
  const [batchSize, setBatchSize] = useState(32);
  const [learningRate, setLearningRate] = useState(0.001);
  const [aeContamination, setAeContamination] = useState(0.05);
  const [algorithmFilter, setAlgorithmFilter] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");

  const trainingError = useMemo(() => {
    if (!trainMutation.error) {
      return "";
    }
    if (axios.isAxiosError(trainMutation.error)) {
      return (trainMutation.error.response?.data as { detail?: string } | undefined)?.detail ?? trainMutation.error.message;
    }
    return "Training failed.";
  }, [trainMutation.error]);

  const filteredModels = useMemo(() => {
    return (modelsQuery.data ?? []).filter((model) => {
      const algorithmMatch = algorithmFilter === "all" || model.algorithm === algorithmFilter;
      const statusMatch = statusFilter === "all" || model.status === statusFilter;
      return algorithmMatch && statusMatch;
    });
  }, [algorithmFilter, statusFilter, modelsQuery.data]);

  const onSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!datasetId || !modelName.trim()) {
      return;
    }

    let hyperparameters: Record<string, unknown>;
    if (algorithm === "isolation_forest") {
      hyperparameters = {
        n_estimators: nEstimators,
        contamination,
      };
    } else if (algorithm === "one_class_svm") {
      hyperparameters = {
        kernel,
        nu,
        gamma,
      };
    } else {
      hyperparameters = {
        hidden_dim: hiddenDim,
        epochs,
        batch_size: batchSize,
        learning_rate: learningRate,
        contamination: aeContamination,
      };
    }

    trainMutation.mutate(
      {
        dataset_id: datasetId,
        model_name: modelName.trim(),
        algorithm,
        hyperparameters,
      },
      {
        onSuccess: () => {
          setModelName("");
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
          <h2 className="text-lg font-semibold text-slate-100">Train Model</h2>
          <p className="mt-1 text-sm text-slate-400">Choose dataset, algorithm, and algorithm-specific hyperparameters.</p>

          <form className="mt-4 space-y-4" onSubmit={onSubmit}>
            <label className="block space-y-1">
              <span className="text-sm text-slate-300">Dataset</span>
              <select
                className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none ring-emerald-400 transition focus:ring"
                value={datasetId}
                onChange={(event) => setDatasetId(event.target.value)}
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
              <span className="text-sm text-slate-300">Algorithm</span>
              <select
                className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none ring-emerald-400 transition focus:ring"
                value={algorithm}
                onChange={(event) => setAlgorithm(event.target.value as ModelAlgorithm)}
                required
              >
                <option value="isolation_forest">Isolation Forest</option>
                <option value="one_class_svm">One-Class SVM</option>
                <option value="autoencoder">Autoencoder</option>
              </select>
            </label>

            <label className="block space-y-1">
              <span className="text-sm text-slate-300">Model Name</span>
              <input
                className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none ring-emerald-400 transition focus:ring"
                placeholder={
                  algorithm === "isolation_forest"
                    ? "Isolation Forest - Auth"
                    : algorithm === "one_class_svm"
                      ? "One-Class SVM - Auth"
                      : "Autoencoder - Auth"
                }
                value={modelName}
                onChange={(event) => setModelName(event.target.value)}
                required
              />
            </label>

            {algorithm === "isolation_forest" ? (
              <div className="grid grid-cols-2 gap-3">
                <label className="space-y-1">
                  <span className="text-sm text-slate-300">n_estimators</span>
                  <input
                    className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none ring-emerald-400 transition focus:ring"
                    type="number"
                    min={10}
                    max={1000}
                    value={nEstimators}
                    onChange={(event) => setNEstimators(Number(event.target.value))}
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
                    value={contamination}
                    onChange={(event) => setContamination(Number(event.target.value))}
                    required
                  />
                </label>
              </div>
            ) : algorithm === "one_class_svm" ? (
              <div className="grid grid-cols-3 gap-3">
                <label className="space-y-1">
                  <span className="text-sm text-slate-300">kernel</span>
                  <select
                    className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none ring-emerald-400 transition focus:ring"
                    value={kernel}
                    onChange={(event) => setKernel(event.target.value)}
                    required
                  >
                    <option value="rbf">rbf</option>
                    <option value="linear">linear</option>
                    <option value="poly">poly</option>
                    <option value="sigmoid">sigmoid</option>
                  </select>
                </label>

                <label className="space-y-1">
                  <span className="text-sm text-slate-300">nu</span>
                  <input
                    className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none ring-emerald-400 transition focus:ring"
                    type="number"
                    min={0.001}
                    max={1}
                    step={0.001}
                    value={nu}
                    onChange={(event) => setNu(Number(event.target.value))}
                    required
                  />
                </label>

                <label className="space-y-1">
                  <span className="text-sm text-slate-300">gamma</span>
                  <select
                    className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none ring-emerald-400 transition focus:ring"
                    value={gamma}
                    onChange={(event) => setGamma(event.target.value)}
                    required
                  >
                    <option value="scale">scale</option>
                    <option value="auto">auto</option>
                  </select>
                </label>
              </div>
            ) : (
              <div className="grid grid-cols-2 gap-3">
                <label className="space-y-1">
                  <span className="text-sm text-slate-300">hidden_dim</span>
                  <input
                    className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none ring-emerald-400 transition focus:ring"
                    type="number"
                    min={2}
                    max={512}
                    value={hiddenDim}
                    onChange={(event) => setHiddenDim(Number(event.target.value))}
                    required
                  />
                </label>

                <label className="space-y-1">
                  <span className="text-sm text-slate-300">epochs</span>
                  <input
                    className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none ring-emerald-400 transition focus:ring"
                    type="number"
                    min={10}
                    max={1000}
                    value={epochs}
                    onChange={(event) => setEpochs(Number(event.target.value))}
                    required
                  />
                </label>

                <label className="space-y-1">
                  <span className="text-sm text-slate-300">batch_size</span>
                  <input
                    className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none ring-emerald-400 transition focus:ring"
                    type="number"
                    min={1}
                    max={4096}
                    value={batchSize}
                    onChange={(event) => setBatchSize(Number(event.target.value))}
                    required
                  />
                </label>

                <label className="space-y-1">
                  <span className="text-sm text-slate-300">learning_rate</span>
                  <input
                    className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none ring-emerald-400 transition focus:ring"
                    type="number"
                    min={0.0001}
                    max={1}
                    step={0.0001}
                    value={learningRate}
                    onChange={(event) => setLearningRate(Number(event.target.value))}
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
                    value={aeContamination}
                    onChange={(event) => setAeContamination(Number(event.target.value))}
                    required
                  />
                </label>
              </div>
            )}

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

          <div className="mb-3 flex items-center justify-between">
            <p className="text-xs text-slate-400">{filteredModels.length} result(s)</p>
            <button
              className="rounded-md border border-slate-700 px-3 py-1 text-xs text-slate-300 hover:bg-slate-800"
              type="button"
              onClick={() => {
                setAlgorithmFilter("all");
                setStatusFilter("all");
              }}
            >
              Reset Filters
            </button>
          </div>

          <div className="mb-4 grid gap-3 sm:grid-cols-2">
            <label className="space-y-1">
              <span className="text-xs uppercase tracking-wide text-slate-400">Filter Algorithm</span>
              <select
                className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none ring-emerald-400 transition focus:ring"
                value={algorithmFilter}
                onChange={(event) => setAlgorithmFilter(event.target.value)}
              >
                <option value="all">All Algorithms</option>
                <option value="isolation_forest">Isolation Forest</option>
                <option value="one_class_svm">One-Class SVM</option>
                <option value="autoencoder">Autoencoder</option>
              </select>
            </label>

            <label className="space-y-1">
              <span className="text-xs uppercase tracking-wide text-slate-400">Filter Status</span>
              <select
                className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none ring-emerald-400 transition focus:ring"
                value={statusFilter}
                onChange={(event) => setStatusFilter(event.target.value)}
              >
                <option value="all">All Statuses</option>
                <option value="ready">Ready</option>
                <option value="training">Training</option>
                <option value="error">Error</option>
              </select>
            </label>
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
                  {filteredModels.map((model) => (
                    <tr className="border-b border-slate-800/80 text-slate-200" key={model.id}>
                      <td className="px-2 py-3">
                        <p className="font-medium">{model.name}</p>
                        <p className="text-xs text-slate-400">{model.id.slice(0, 8)}</p>
                      </td>
                      <td className="px-2 py-3">
                        <span
                          className={[
                            "inline-flex rounded-full border px-2 py-1 text-xs font-medium",
                            model.algorithm === "autoencoder"
                              ? "border-violet-500/30 bg-violet-500/10 text-violet-300"
                              : model.algorithm === "one_class_svm"
                              ? "border-cyan-500/30 bg-cyan-500/10 text-cyan-300"
                              : "border-emerald-500/30 bg-emerald-500/10 text-emerald-300",
                          ].join(" ")}
                        >
                          {formatAlgorithmLabel(model.algorithm)}
                        </span>
                        <p className="mt-1 text-xs text-slate-400">{previewHyperparameters(model.hyperparameters)}</p>
                      </td>
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

              {filteredModels.length === 0 ? (
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
