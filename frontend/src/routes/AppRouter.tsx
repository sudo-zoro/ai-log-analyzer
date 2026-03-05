import { useState } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import DashboardLayout from "../components/layout/DashboardLayout";
import Dashboard from "../pages/Dashboard/Dashboard";
import DetectionPage from "../pages/Detection/DetectionPage";
import DatasetsPage from "../pages/Datasets/DatasetsPage";
import InsightsPage from "../pages/Insights/InsightsPage";
import ModelsPage from "../pages/Models/ModelsPage";
import type { DetectionRun } from "../types/detection";

function AppRouter() {
  const [selectedDetection, setSelectedDetection] = useState<DetectionRun | null>(null);

  return (
    <DashboardLayout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/datasets" element={<DatasetsPage />} />
        <Route path="/models" element={<ModelsPage />} />
        <Route
          path="/detection"
          element={
            <DetectionPage selectedDetection={selectedDetection} onDetectionComplete={setSelectedDetection} />
          }
        />
        <Route path="/insights" element={<InsightsPage selectedDetection={selectedDetection} />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </DashboardLayout>
  );
}

export default AppRouter;
