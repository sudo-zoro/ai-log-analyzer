"""
Model Trainer Module.

Trains anomaly detection models on CSV datasets, persists artifacts,
and returns training metrics.
"""
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from sklearn.ensemble import IsolationForest
from sklearn.neural_network import MLPRegressor
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler
from app.ml_engine.feature_engineering import engineer_features
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


def train_one_class_svm(
    dataset_path: str,
    model_save_path: str,
    scaler_save_path: str,
    kernel: str = "rbf",
    nu: float = 0.05,
    gamma: str | float = "scale",
) -> dict:
    """
    Train a One-Class SVM on a CSV log dataset.

    Returns a metrics dict:
        {
            "kernel": str,
            "nu": float,
            "gamma": str|float,
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
    logger.info("Training One-Class SVM on %d samples, %d features", X.shape[0], X.shape[1])

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = OneClassSVM(kernel=kernel, nu=nu, gamma=gamma)
    model.fit(X_scaled)

    predictions = model.predict(X_scaled)
    anomaly_count = int(np.sum(predictions == -1))
    anomaly_ratio = float(anomaly_count / len(predictions))

    Path(model_save_path).parent.mkdir(parents=True, exist_ok=True)
    Path(scaler_save_path).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_save_path)
    joblib.dump(scaler, scaler_save_path)
    logger.info("Saved model to %s", model_save_path)
    logger.info("Saved scaler to %s", scaler_save_path)

    return {
        "kernel": kernel,
        "nu": nu,
        "gamma": gamma,
        "total_samples": int(X.shape[0]),
        "feature_count": int(X.shape[1]),
        "feature_columns": feature_columns,
        "predicted_anomaly_count": anomaly_count,
        "predicted_anomaly_ratio": anomaly_ratio,
    }


def train_autoencoder(
    dataset_path: str,
    model_save_path: str,
    scaler_save_path: str,
    hidden_dim: int = 16,
    epochs: int = 80,
    batch_size: int = 32,
    learning_rate: float = 0.001,
    contamination: float = 0.05,
    random_state: int = 42,
) -> dict:
    """
    Train an MLP-based autoencoder (reconstruction model) on CSV logs.

    Returns a metrics dict including reconstruction threshold used
    to classify anomalies.
    """
    logger.info("Loading dataset from %s", dataset_path)
    df = pd.read_csv(dataset_path)

    feature_df = engineer_features(df)
    feature_columns = list(feature_df.columns)
    X = feature_df.values

    logger.info("Training autoencoder on %d samples, %d features", X.shape[0], X.shape[1])
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = MLPRegressor(
        hidden_layer_sizes=(hidden_dim,),
        activation="relu",
        solver="adam",
        learning_rate_init=learning_rate,
        max_iter=epochs,
        batch_size=min(batch_size, max(1, X_scaled.shape[0])),
        random_state=random_state,
    )
    model.fit(X_scaled, X_scaled)

    recon = model.predict(X_scaled)
    reconstruction_errors = np.mean(np.square(X_scaled - recon), axis=1)
    threshold = float(np.percentile(reconstruction_errors, 100 * (1 - contamination)))
    anomaly_mask = reconstruction_errors > threshold
    anomaly_count = int(np.sum(anomaly_mask))
    anomaly_ratio = float(anomaly_count / len(reconstruction_errors))

    Path(model_save_path).parent.mkdir(parents=True, exist_ok=True)
    Path(scaler_save_path).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_save_path)
    joblib.dump(scaler, scaler_save_path)
    logger.info("Saved model to %s", model_save_path)
    logger.info("Saved scaler to %s", scaler_save_path)

    return {
        "hidden_dim": hidden_dim,
        "epochs": epochs,
        "batch_size": batch_size,
        "learning_rate": learning_rate,
        "contamination": contamination,
        "reconstruction_threshold": threshold,
        "total_samples": int(X.shape[0]),
        "feature_count": int(X.shape[1]),
        "feature_columns": feature_columns,
        "predicted_anomaly_count": anomaly_count,
        "predicted_anomaly_ratio": anomaly_ratio,
    }
