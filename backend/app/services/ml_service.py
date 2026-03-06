"""
ML Model Service — training orchestration and model registry management.
"""
import uuid
from pathlib import Path
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.ml_model import MLModel
from app.models.dataset import Dataset
from app.ml_engine.trainer import train_autoencoder, train_isolation_forest, train_one_class_svm
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)
SUPPORTED_ALGORITHMS = {"isolation_forest", "one_class_svm", "autoencoder"}


def start_training(
    db: Session,
    dataset_id: str,
    model_name: str,
    algorithm: str = "isolation_forest",
    hyperparameters: dict | None = None,
) -> MLModel:
    """Train a selected anomaly model on a dataset and register it."""
    if algorithm not in SUPPORTED_ALGORITHMS:
        raise HTTPException(status_code=400, detail=f"Unsupported algorithm '{algorithm}'.")

    # Lookup dataset
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found.")
    if dataset.status != "validated":
        raise HTTPException(status_code=400, detail=f"Dataset status is '{dataset.status}', expected 'validated'.")

    params = _build_hyperparameters(algorithm=algorithm, hyperparameters=hyperparameters or {})

    # Create model record (pending)
    run_id = str(uuid.uuid4())
    model_dir = Path(settings.MODELS_DIR) / run_id
    model_dir.mkdir(parents=True, exist_ok=True)

    ml_model = MLModel(
        id=run_id,
        name=model_name,
        algorithm=algorithm,
        dataset_id=dataset_id,
        model_path=str(model_dir / "model.joblib"),
        scaler_path=str(model_dir / "scaler.joblib"),
        hyperparameters=params,
        status="training",
    )
    db.add(ml_model)
    db.commit()

    try:
        if algorithm == "isolation_forest":
            metrics = train_isolation_forest(
                dataset_path=dataset.file_path,
                model_save_path=ml_model.model_path,
                scaler_save_path=ml_model.scaler_path,
                n_estimators=int(params["n_estimators"]),
                contamination=float(params["contamination"]),
            )
        elif algorithm == "one_class_svm":
            metrics = train_one_class_svm(
                dataset_path=dataset.file_path,
                model_save_path=ml_model.model_path,
                scaler_save_path=ml_model.scaler_path,
                kernel=str(params["kernel"]),
                nu=float(params["nu"]),
                gamma=params["gamma"],
            )
        elif algorithm == "autoencoder":
            metrics = train_autoencoder(
                dataset_path=dataset.file_path,
                model_save_path=ml_model.model_path,
                scaler_save_path=ml_model.scaler_path,
                hidden_dim=int(params["hidden_dim"]),
                epochs=int(params["epochs"]),
                batch_size=int(params["batch_size"]),
                learning_rate=float(params["learning_rate"]),
                contamination=float(params["contamination"]),
            )
        else:
            raise ValueError(f"Unsupported algorithm '{algorithm}'.")

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


def _build_hyperparameters(algorithm: str, hyperparameters: dict) -> dict:
    """Normalize and validate per-algorithm hyperparameters."""
    if algorithm == "isolation_forest":
        n_estimators = int(hyperparameters.get("n_estimators", 100))
        contamination = float(hyperparameters.get("contamination", 0.05))
        if n_estimators < 10 or n_estimators > 1000:
            raise HTTPException(status_code=422, detail="n_estimators must be between 10 and 1000.")
        if contamination <= 0.0 or contamination > 0.5:
            raise HTTPException(status_code=422, detail="contamination must be > 0 and <= 0.5.")
        return {"n_estimators": n_estimators, "contamination": contamination}

    if algorithm == "one_class_svm":
        kernel = str(hyperparameters.get("kernel", "rbf"))
        nu = float(hyperparameters.get("nu", 0.05))
        gamma = hyperparameters.get("gamma", "scale")

        allowed_kernels = {"linear", "poly", "rbf", "sigmoid"}
        if kernel not in allowed_kernels:
            raise HTTPException(status_code=422, detail=f"kernel must be one of {sorted(allowed_kernels)}.")
        if nu <= 0.0 or nu > 1.0:
            raise HTTPException(status_code=422, detail="nu must be > 0 and <= 1.")
        if not (gamma == "scale" or gamma == "auto" or isinstance(gamma, int | float)):
            raise HTTPException(status_code=422, detail="gamma must be 'scale', 'auto', or numeric.")

        return {"kernel": kernel, "nu": nu, "gamma": gamma}

    if algorithm == "autoencoder":
        hidden_dim = int(hyperparameters.get("hidden_dim", 16))
        epochs = int(hyperparameters.get("epochs", 80))
        batch_size = int(hyperparameters.get("batch_size", 32))
        learning_rate = float(hyperparameters.get("learning_rate", 0.001))
        contamination = float(hyperparameters.get("contamination", 0.05))

        if hidden_dim < 2 or hidden_dim > 512:
            raise HTTPException(status_code=422, detail="hidden_dim must be between 2 and 512.")
        if epochs < 10 or epochs > 1000:
            raise HTTPException(status_code=422, detail="epochs must be between 10 and 1000.")
        if batch_size < 1 or batch_size > 4096:
            raise HTTPException(status_code=422, detail="batch_size must be between 1 and 4096.")
        if learning_rate <= 0 or learning_rate > 1:
            raise HTTPException(status_code=422, detail="learning_rate must be > 0 and <= 1.")
        if contamination <= 0.0 or contamination > 0.5:
            raise HTTPException(status_code=422, detail="contamination must be > 0 and <= 0.5.")

        return {
            "hidden_dim": hidden_dim,
            "epochs": epochs,
            "batch_size": batch_size,
            "learning_rate": learning_rate,
            "contamination": contamination,
        }

    raise HTTPException(status_code=400, detail=f"Unsupported algorithm '{algorithm}'.")
