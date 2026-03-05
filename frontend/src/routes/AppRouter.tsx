import { Navigate, Route, Routes } from "react-router-dom";
import DashboardLayout from "../components/layout/DashboardLayout";
import Dashboard from "../pages/Dashboard/Dashboard";

function PlaceholderPage({ title }: { title: string }) {
  return (
    <section className="rounded-xl border border-slate-800 bg-slate-900/60 p-6">
      <h1 className="text-2xl font-semibold text-white">{title}</h1>
      <p className="mt-2 text-slate-400">This module will be implemented in the next phase.</p>
    </section>
  );
}

function AppRouter() {
  return (
    <DashboardLayout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/datasets" element={<PlaceholderPage title="Datasets" />} />
        <Route path="/models" element={<PlaceholderPage title="Models" />} />
        <Route path="/detection" element={<PlaceholderPage title="Detection" />} />
        <Route path="/insights" element={<PlaceholderPage title="AI Insights" />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </DashboardLayout>
  );
}

export default AppRouter;
