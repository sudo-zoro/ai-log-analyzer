"""
Anomaly Detection Inference Module.

Loads a trained Isolation Forest model and scaler from disk,
applies feature engineering, and produces anomaly labels + scores.
"""
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from typing import Any
from app.ml_engine.feature_engineering import engineer_features
from app.core.logging import get_logger

logger = get_logger(__name__)


def load_artifacts(model_path: str, scaler_path: str) -> tuple[Any, Any]:
    """Load model and scaler from disk."""
    if not Path(model_path).exists():
        raise FileNotFoundError(f"Model file not found: {model_path}")
    if not Path(scaler_path).exists():
        raise FileNotFoundError(f"Scaler file not found: {scaler_path}")

    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
    logger.info("Loaded model from %s", model_path)
    return model, scaler


def run_detection(
    df: pd.DataFrame,
    model_path: str,
    scaler_path: str,
    feature_columns: list[str],
    algorithm: str = "isolation_forest",
    hyperparameters: dict | None = None,
    metrics: dict | None = None,
) -> dict:
    """
    Run anomaly detection on a log DataFrame.

    Returns:
        {
            "total_rows": int,
            "anomaly_count": int,
            "anomaly_ratio": float,
            "anomalies": [ { "row_index": int, "score": float, "raw_row": dict } ],
            "all_scores": [float, ...],   # one per row
            "predictions": [int, ...]     # -1=anomaly, 1=normal
        }
    """
    model, scaler = load_artifacts(model_path, scaler_path)

    feature_df = engineer_features(df)

    # Align feature columns to what was used during training
    for col in feature_columns:
        if col not in feature_df.columns:
            feature_df[col] = 0.0
    feature_df = feature_df[feature_columns]

    X = scaler.transform(feature_df.values)

    if algorithm in {"isolation_forest", "one_class_svm"}:
        predictions = model.predict(X)  # 1=normal, -1=anomaly
        scores = model.decision_function(X)  # lower = more anomalous
    elif algorithm == "autoencoder":
        recon = model.predict(X)
        reconstruction_errors = np.mean(np.square(X - recon), axis=1)
        threshold = float((metrics or {}).get("reconstruction_threshold", 0.0))

        if threshold <= 0:
            contamination = float((hyperparameters or {}).get("contamination", 0.05))
            threshold = float(np.percentile(reconstruction_errors, 100 * (1 - contamination)))

        predictions = np.where(reconstruction_errors > threshold, -1, 1)
        # Lower score should mean more anomalous for consistent sorting.
        scores = threshold - reconstruction_errors
    else:
        raise ValueError(f"Unsupported algorithm '{algorithm}'.")

    total_rows = len(df)
    anomaly_mask = predictions == -1
    anomaly_indices = np.where(anomaly_mask)[0].tolist()
    anomaly_count = len(anomaly_indices)

    anomalies = []
    for idx in anomaly_indices:
        anomalies.append({
            "row_index": idx,
            "score": float(scores[idx]),
            "raw_row": df.iloc[idx].fillna("").astype(str).to_dict(),
        })

    # Sort by most anomalous first (lowest score)
    anomalies.sort(key=lambda x: x["score"])

    logger.info(
        "Detection complete: %d/%d anomalies (%.1f%%)",
        anomaly_count, total_rows, (anomaly_count / total_rows * 100) if total_rows else 0,
    )

    return {
        "total_rows": total_rows,
        "anomaly_count": anomaly_count,
        "anomaly_ratio": float(anomaly_count / total_rows) if total_rows else 0.0,
        "anomalies": anomalies,
        "all_scores": scores.tolist(),
        "predictions": predictions.tolist(),
    }
