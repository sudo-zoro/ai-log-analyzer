"""ML model training and registry API routes."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Any
from app.core.database import get_db
from app.services import ml_service

router = APIRouter()


class TrainRequest(BaseModel):
    dataset_id: str
    model_name: str
    algorithm: str = Field(default="isolation_forest")
    hyperparameters: dict[str, Any] | None = None


class ModelResponse(BaseModel):
    id: str
    name: str
    algorithm: str
    dataset_id: str | None
    status: str
    hyperparameters: dict[str, Any] | None
    metrics: dict[str, Any] | None
    feature_columns: list[str] | None
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("/train", response_model=ModelResponse, status_code=201)
def train_model(request: TrainRequest, db: Session = Depends(get_db)):
    """Train a supported anomaly model on a dataset."""
    return ml_service.start_training(
        db=db,
        dataset_id=request.dataset_id,
        model_name=request.model_name,
        algorithm=request.algorithm,
        hyperparameters=request.hyperparameters,
    )


@router.get("/", response_model=list[ModelResponse])
def list_models(db: Session = Depends(get_db)):
    """List all trained models."""
    return ml_service.list_models(db)


@router.get("/{model_id}", response_model=ModelResponse)
def get_model(model_id: str, db: Session = Depends(get_db)):
    """Get a specific model by ID."""
    return ml_service.get_model(db, model_id)


@router.delete("/{model_id}", status_code=204)
def delete_model(model_id: str, db: Session = Depends(get_db)):
    """Delete a model and its artifact files."""
    ml_service.delete_model(db, model_id)
