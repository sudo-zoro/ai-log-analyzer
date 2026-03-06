export type ModelAlgorithm = "isolation_forest" | "one_class_svm" | "autoencoder";

export type TrainModelPayload = {
  dataset_id: string;
  model_name: string;
  algorithm: ModelAlgorithm;
  hyperparameters: Record<string, unknown>;
};

export type ModelMetrics = {
  n_estimators?: number;
  contamination?: number;
  kernel?: string;
  nu?: number;
  gamma?: string | number;
  hidden_dim?: number;
  epochs?: number;
  batch_size?: number;
  learning_rate?: number;
  reconstruction_threshold?: number;
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
