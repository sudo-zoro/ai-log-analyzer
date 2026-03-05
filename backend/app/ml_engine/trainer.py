"""
Isolation Forest Trainer Module.

Trains an anomaly detection model on a CSV dataset,
persists model + scaler to disk, and returns training metrics.
"""
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from app.ml_engine.feature_engineering import engineer_features, get_feature_columns
from app.core.logging import get_logger

logger = get_logger(__name__)


def train_isolation_forest(
    dataset_path: str,
    model_save_path: str,
    scaler_save_path: str,
    n_estimators: int = 100,
    contamination: float = 0.05,
    random_state: int = 42,
) -> dict:
    """
    Train an Isolation Forest on a CSV log dataset.

    Returns a metrics dict:
        {
            "n_estimators": int,
            "contamination": float,
            "total_samples": int,
            "feature_count": int,
            "feature_columns": [str, ...],
            "predicted_anomaly_count": int,
            "predicted_anomaly_ratio": float,
        }
    """
    logger.info("Loading dataset from %s", dataset_path)
    df = pd.read_csv(dataset_path)

    feature_df = engineer_features(df)
    feature_columns = list(feature_df.columns)

    X = feature_df.values
    logger.info("Training on %d samples, %d features", X.shape[0], X.shape[1])

    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Train model
    model = IsolationForest(
        n_estimators=n_estimators,
        contamination=contamination,
        random_state=random_state,
        n_jobs=-1,
    )
    model.fit(X_scaled)

    # Compute training-time anomaly stats
    predictions = model.predict(X_scaled)
    anomaly_count = int(np.sum(predictions == -1))
    anomaly_ratio = float(anomaly_count / len(predictions))

    # Persist artifacts
    Path(model_save_path).parent.mkdir(parents=True, exist_ok=True)
    Path(scaler_save_path).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_save_path)
    joblib.dump(scaler, scaler_save_path)
    logger.info("Saved model to %s", model_save_path)
    logger.info("Saved scaler to %s", scaler_save_path)

    return {
        "n_estimators": n_estimators,
        "contamination": contamination,
        "total_samples": int(X.shape[0]),
        "feature_count": int(X.shape[1]),
        "feature_columns": feature_columns,
        "predicted_anomaly_count": anomaly_count,
        "predicted_anomaly_ratio": anomaly_ratio,
    }
