"""
ML Model Service — training orchestration and model registry management.
"""
import uuid
import os
from pathlib import Path
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.ml_model import MLModel
from app.models.dataset import Dataset
from app.ml_engine.trainer import train_isolation_forest
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def start_training(
    db: Session,
    dataset_id: str,
    model_name: str,
    n_estimators: int = 100,
    contamination: float = 0.05,
) -> MLModel:
    """Train an Isolation Forest on a dataset and register the model."""
    # Lookup dataset
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found.")
    if dataset.status != "validated":
        raise HTTPException(status_code=400, detail=f"Dataset status is '{dataset.status}', expected 'validated'.")

    # Create model record (pending)
    run_id = str(uuid.uuid4())
    model_dir = Path(settings.MODELS_DIR) / run_id
    model_dir.mkdir(parents=True, exist_ok=True)

    ml_model = MLModel(
        id=run_id,
        name=model_name,
        algorithm="isolation_forest",
        dataset_id=dataset_id,
        model_path=str(model_dir / "model.joblib"),
        scaler_path=str(model_dir / "scaler.joblib"),
        hyperparameters={"n_estimators": n_estimators, "contamination": contamination},
        status="training",
    )
    db.add(ml_model)
    db.commit()

    try:
        metrics = train_isolation_forest(
            dataset_path=dataset.file_path,
            model_save_path=ml_model.model_path,
            scaler_save_path=ml_model.scaler_path,
            n_estimators=n_estimators,
            contamination=contamination,
        )
        ml_model.feature_columns = metrics.pop("feature_columns")
        ml_model.metrics = metrics
        ml_model.status = "ready"
        logger.info("Model %s training complete", run_id)
    except Exception as e:
        ml_model.status = "error"
        ml_model.error_message = str(e)
        logger.error("Model %s training failed: %s", run_id, e)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")

    db.commit()
    db.refresh(ml_model)
    return ml_model


def list_models(db: Session) -> list[MLModel]:
    return db.query(MLModel).order_by(MLModel.created_at.desc()).all()


def get_model(db: Session, model_id: str) -> MLModel:
    m = db.query(MLModel).filter(MLModel.id == model_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Model not found.")
    return m


def delete_model(db: Session, model_id: str) -> None:
    m = get_model(db, model_id)
    for path in [m.model_path, m.scaler_path]:
        if path:
            Path(path).unlink(missing_ok=True)
    db.delete(m)
    db.commit()
    logger.info("Model %s deleted", model_id)
