import { useMemo, useState } from "react";
import axios from "axios";
import { useDatasets, useDeleteDataset, useUploadDataset } from "../../hooks/useDatasets";
import { formatBytes, formatDateTime } from "../../utils/format";

function DatasetsPage() {
  const [datasetName, setDatasetName] = useState("");
  const [file, setFile] = useState<File | null>(null);

  const datasetsQuery = useDatasets();
  const uploadMutation = useUploadDataset();
  const deleteMutation = useDeleteDataset();

  const errorMessage = useMemo(() => {
    if (!uploadMutation.error) {
      return "";
    }
    if (axios.isAxiosError(uploadMutation.error)) {
      return (uploadMutation.error.response?.data as { detail?: string } | undefined)?.detail ?? uploadMutation.error.message;
    }
    return "Upload failed.";
  }, [uploadMutation.error]);

  const onSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!datasetName.trim() || !file) {
      return;
    }

    uploadMutation.mutate(
      { name: datasetName.trim(), file },
      {
        onSuccess: () => {
          setDatasetName("");
          setFile(null);
          event.currentTarget.reset();
        },
      },
    );
  };

  return (
    <section className="space-y-6">
      <header>
        <p className="text-xs uppercase tracking-[0.2em] text-cyan-300/80">Datasets</p>
        <h1 className="text-3xl font-semibold text-white">Upload and Manage Log Datasets</h1>
      </header>

      <div className="grid gap-6 lg:grid-cols-[1fr_1.6fr]">
        <article className="rounded-xl border border-slate-800 bg-slate-900/60 p-5">
          <h2 className="text-lg font-semibold text-slate-100">New Dataset</h2>
          <p className="mt-1 text-sm text-slate-400">Upload a CSV file to prepare model training.</p>

          <form className="mt-4 space-y-4" onSubmit={onSubmit}>
            <label className="block space-y-1">
              <span className="text-sm text-slate-300">Dataset Name</span>
              <input
                className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none ring-cyan-400 transition focus:ring"
                placeholder="Auth Logs - March"
                value={datasetName}
                onChange={(event) => setDatasetName(event.target.value)}
                required
              />
            </label>

            <label className="block space-y-1">
              <span className="text-sm text-slate-300">CSV File</span>
              <input
                className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-300 file:mr-3 file:rounded-md file:border-0 file:bg-cyan-500/20 file:px-3 file:py-2 file:text-cyan-300"
                type="file"
                accept=".csv"
                onChange={(event) => setFile(event.target.files?.[0] ?? null)}
                required
              />
            </label>

            {errorMessage ? <p className="text-sm text-rose-400">{errorMessage}</p> : null}

            <button
              className="rounded-lg bg-cyan-500 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-cyan-400 disabled:cursor-not-allowed disabled:bg-slate-700 disabled:text-slate-400"
              type="submit"
              disabled={uploadMutation.isPending}
            >
              {uploadMutation.isPending ? "Uploading..." : "Upload Dataset"}
            </button>
          </form>
        </article>

        <article className="rounded-xl border border-slate-800 bg-slate-900/60 p-5">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-slate-100">Dataset Registry</h2>
            <span className="rounded-full border border-slate-700 px-3 py-1 text-xs text-slate-300">
              {datasetsQuery.data?.length ?? 0} total
            </span>
          </div>

          {datasetsQuery.isLoading ? <p className="text-slate-400">Loading datasets...</p> : null}
          {datasetsQuery.isError ? <p className="text-rose-400">Failed to load datasets.</p> : null}

          {!datasetsQuery.isLoading && !datasetsQuery.isError ? (
            <div className="overflow-x-auto">
              <table className="min-w-full text-left text-sm">
                <thead className="text-xs uppercase tracking-wide text-slate-400">
                  <tr className="border-b border-slate-800">
                    <th className="px-2 py-2">Name</th>
                    <th className="px-2 py-2">Rows</th>
                    <th className="px-2 py-2">Columns</th>
                    <th className="px-2 py-2">Size</th>
                    <th className="px-2 py-2">Created</th>
                    <th className="px-2 py-2">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {(datasetsQuery.data ?? []).map((dataset) => (
                    <tr className="border-b border-slate-800/80 text-slate-200" key={dataset.id}>
                      <td className="px-2 py-3">
                        <p className="font-medium">{dataset.name}</p>
                        <p className="text-xs text-slate-400">{dataset.original_filename}</p>
                      </td>
                      <td className="px-2 py-3">{dataset.row_count ?? "-"}</td>
                      <td className="px-2 py-3">{dataset.column_count ?? "-"}</td>
                      <td className="px-2 py-3">{formatBytes(dataset.file_size_bytes)}</td>
                      <td className="px-2 py-3">{formatDateTime(dataset.created_at)}</td>
                      <td className="px-2 py-3">
                        <button
                          className="rounded-md border border-rose-500/40 px-3 py-1 text-xs text-rose-300 hover:bg-rose-500/10 disabled:cursor-not-allowed disabled:opacity-50"
                          onClick={() => deleteMutation.mutate(dataset.id)}
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

              {(datasetsQuery.data ?? []).length === 0 ? (
                <p className="py-6 text-center text-sm text-slate-400">No datasets uploaded yet.</p>
              ) : null}
            </div>
          ) : null}
        </article>
      </div>
    </section>
  );
}

export default DatasetsPage;
