import { useAnalysisSession } from "../../context/AnalysisSessionContext";
import type { DetectionRun } from "../../types/detection";

type InsightsPageProps = {
  selectedDetection: DetectionRun | null;
};

function InsightsPage({ selectedDetection }: InsightsPageProps) {
  const { generateDetectionInsights, insights, insightsError, isGeneratingInsights } = useAnalysisSession();
  const anomalies = selectedDetection?.results?.anomalies ?? [];

  const onGenerate = () => {
    if (!selectedDetection || anomalies.length === 0) {
      return;
    }

    generateDetectionInsights({
      anomaly_rows: anomalies.map((item) => item.raw_row),
      anomaly_count: selectedDetection.anomaly_count ?? anomalies.length,
      anomaly_ratio: selectedDetection.anomaly_ratio ?? 0,
    });
  };

  const data = insights;

  return (
    <section className="space-y-6">
      <header>
        <p className="text-xs uppercase tracking-[0.2em] text-cyan-300/80">AI Insights</p>
        <h1 className="text-3xl font-semibold text-white">RAG + LLM Security Explanation</h1>
      </header>

      <article className="rounded-xl border border-slate-800 bg-slate-900/60 p-5">
        {selectedDetection ? (
          <div className="space-y-4">
            <div className="grid gap-3 sm:grid-cols-3">
              <div className="rounded-lg border border-slate-800 bg-slate-950/70 p-3">
                <p className="text-xs text-slate-400">Detection Run</p>
                <p className="mt-1 text-sm font-semibold">{selectedDetection.id.slice(0, 8)}</p>
              </div>
              <div className="rounded-lg border border-slate-800 bg-slate-950/70 p-3">
                <p className="text-xs text-slate-400">Anomalies</p>
                <p className="mt-1 text-sm font-semibold text-amber-300">{selectedDetection.anomaly_count ?? 0}</p>
              </div>
              <div className="rounded-lg border border-slate-800 bg-slate-950/70 p-3">
                <p className="text-xs text-slate-400">Anomaly Ratio</p>
                <p className="mt-1 text-sm font-semibold">{((selectedDetection.anomaly_ratio ?? 0) * 100).toFixed(2)}%</p>
              </div>
            </div>

            <button
              className="rounded-lg bg-cyan-400 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:bg-slate-700 disabled:text-slate-400"
              type="button"
              onClick={onGenerate}
              disabled={anomalies.length === 0 || isGeneratingInsights}
            >
              {isGeneratingInsights ? "Generating..." : "Generate AI Explanation"}
            </button>
          </div>
        ) : (
          <p className="text-slate-400">No detection result selected. Run detection first and then open AI Insights.</p>
        )}

        {insightsError ? <p className="mt-4 text-sm text-rose-400">{insightsError}</p> : null}
      </article>

      {data ? (
        <article className="space-y-4 rounded-xl border border-slate-800 bg-slate-900/60 p-5">
          <div className="grid gap-3 sm:grid-cols-3">
            <div className="rounded-lg border border-slate-800 bg-slate-950/70 p-3">
              <p className="text-xs text-slate-400">Attack Type</p>
              <p className="mt-1 text-sm font-semibold">{data.attack_type ?? "-"}</p>
            </div>
            <div className="rounded-lg border border-slate-800 bg-slate-950/70 p-3">
              <p className="text-xs text-slate-400">Severity</p>
              <p className="mt-1 text-sm font-semibold text-rose-300">{data.severity ?? "-"}</p>
            </div>
            <div className="rounded-lg border border-slate-800 bg-slate-950/70 p-3">
              <p className="text-xs text-slate-400">Risk Level</p>
              <p className="mt-1 text-sm font-semibold text-amber-300">{data.risk_level ?? "-"}</p>
            </div>
          </div>

          <div className="space-y-3">
            <div>
              <h2 className="text-sm font-semibold text-slate-200">Explanation</h2>
              <p className="mt-1 text-sm text-slate-300">{data.explanation ?? "-"}</p>
            </div>
            <div>
              <h2 className="text-sm font-semibold text-slate-200">Recommended Fix</h2>
              <p className="mt-1 text-sm text-slate-300">{data.recommended_fix ?? "-"}</p>
            </div>
            <div>
              <h2 className="text-sm font-semibold text-slate-200">OWASP Category</h2>
              <p className="mt-1 text-sm text-slate-300">{data.owasp_category ?? "-"}</p>
            </div>
            <div>
              <h2 className="text-sm font-semibold text-slate-200">References</h2>
              {data.references && data.references.length > 0 ? (
                <ul className="mt-1 list-disc space-y-1 pl-5 text-sm text-slate-300">
                  {data.references.map((reference) => (
                    <li key={reference}>{reference}</li>
                  ))}
                </ul>
              ) : (
                <p className="mt-1 text-sm text-slate-300">-</p>
              )}
            </div>
          </div>
        </article>
      ) : null}
    </section>
  );
}

export default InsightsPage;
