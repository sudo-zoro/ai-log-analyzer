export type DetectionAnomaly = {
  row_index: number;
  score: number;
  raw_row: Record<string, string>;
};

export type DetectionResults = {
  anomalies: DetectionAnomaly[];
  all_scores: number[];
};

export type DetectionRun = {
  id: string;
  model_id: string;
  total_rows: number | null;
  anomaly_count: number | null;
  anomaly_ratio: number | null;
  status: string;
  results: DetectionResults | null;
  created_at: string;
};

export type RunDetectionPayload = {
  model_id: string;
  file: File;
};
