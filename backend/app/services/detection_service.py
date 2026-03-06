"""
Detection Service — runs anomaly detection using a registered model.
"""
import pandas as pd
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.detection_run import DetectionRun
from app.models.ml_model import MLModel
from app.ml_engine.detector import run_detection
from app.core.logging import get_logger

logger = get_logger(__name__)


def run_detection_job(
    db: Session,
    model_id: str,
    df: pd.DataFrame,
    input_filename: str = "inline",
) -> DetectionRun:
    """Run anomaly detection and persist the result."""
    model = db.query(MLModel).filter(MLModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found.")
    if model.status != "ready":
        raise HTTPException(status_code=400, detail=f"Model status is '{model.status}', expected 'ready'.")

    detection = DetectionRun(
        model_id=model_id,
        input_file=input_filename,
        status="running",
    )
    db.add(detection)
    db.commit()

    try:
        results = run_detection(
            df=df,
            model_path=model.model_path,
            scaler_path=model.scaler_path,
            feature_columns=model.feature_columns or [],
            algorithm=model.algorithm,
            hyperparameters=model.hyperparameters or {},
            metrics=model.metrics or {},
        )
        detection.total_rows = results["total_rows"]
        detection.anomaly_count = results["anomaly_count"]
        detection.anomaly_ratio = results["anomaly_ratio"]
        # Store compact results (anomalies only + scores)
        detection.results = {
            "anomalies": results["anomalies"][:500],   # cap at 500 for DB storage
            "all_scores": results["all_scores"][:2000],
        }
        detection.status = "done"
        logger.info("Detection run %s complete: %d anomalies", detection.id, detection.anomaly_count)
    except HTTPException:
        raise
    except Exception as e:
        detection.status = "error"
        detection.error_message = str(e)
        logger.error("Detection run %s failed: %s", detection.id, e)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")

    db.commit()
    db.refresh(detection)
    return detection


def get_detection_run(db: Session, run_id: str) -> DetectionRun:
    run = db.query(DetectionRun).filter(DetectionRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Detection run not found.")
    return run


def list_detection_runs(db: Session) -> list[DetectionRun]:
    return db.query(DetectionRun).order_by(DetectionRun.created_at.desc()).all()
