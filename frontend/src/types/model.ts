export type TrainModelPayload = {
  dataset_id: string;
  model_name: string;
  n_estimators: number;
  contamination: number;
};

export type ModelMetrics = {
  n_estimators?: number;
  contamination?: number;
  total_samples?: number;
  feature_count?: number;
  predicted_anomaly_count?: number;
  predicted_anomaly_ratio?: number;
};

export type ModelInfo = {
  id: string;
  name: string;
  algorithm: string;
  dataset_id: string | null;
  status: string;
  hyperparameters: Record<string, unknown> | null;
  metrics: ModelMetrics | null;
  feature_columns: string[] | null;
  created_at: string;
};
