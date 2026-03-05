"""Anomaly detection API routes."""
import io
import pandas as pd
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from typing import Any
from app.core.database import get_db
from app.services import detection_service

router = APIRouter()


class AnomalyResult(BaseModel):
    row_index: int
    score: float
    raw_row: dict[str, str]


class DetectionRunResponse(BaseModel):
    id: str
    model_id: str
    total_rows: int | None
    anomaly_count: int | None
    anomaly_ratio: float | None
    status: str
    results: dict[str, Any] | None
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("/", response_model=DetectionRunResponse, status_code=201)
async def run_detection(
    model_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Run anomaly detection on uploaded log CSV using a registered model.
    Returns detection run results including anomaly rows and scores.
    """
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted.")

    contents = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Could not parse CSV: {str(e)}")

    if df.empty:
        raise HTTPException(status_code=422, detail="CSV is empty.")

    return detection_service.run_detection_job(
        db=db,
        model_id=model_id,
        df=df,
        input_filename=file.filename,
    )


@router.get("/", response_model=list[DetectionRunResponse])
def list_detection_runs(db: Session = Depends(get_db)):
    """List all detection runs."""
    return detection_service.list_detection_runs(db)


@router.get("/{run_id}", response_model=DetectionRunResponse)
def get_detection_run(run_id: str, db: Session = Depends(get_db)):
    """Get a specific detection run by ID."""
    return detection_service.get_detection_run(db, run_id)
