"""Dataset management API routes."""
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from app.core.database import get_db
from app.services import dataset_service

router = APIRouter()


class DatasetResponse(BaseModel):
    id: str
    name: str
    original_filename: str
    row_count: int | None
    column_count: int | None
    file_size_bytes: int | None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("/upload", response_model=DatasetResponse, status_code=201)
async def upload_dataset(
    file: UploadFile = File(...),
    name: str = Form(...),
    db: Session = Depends(get_db),
):
    """Upload a CSV log dataset."""
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted.")
    dataset = dataset_service.create_dataset(db, file, name)
    return dataset


@router.get("/", response_model=list[DatasetResponse])
def list_datasets(db: Session = Depends(get_db)):
    """List all uploaded datasets."""
    return dataset_service.list_datasets(db)


@router.get("/{dataset_id}", response_model=DatasetResponse)
def get_dataset(dataset_id: str, db: Session = Depends(get_db)):
    """Get a specific dataset by ID."""
    return dataset_service.get_dataset(db, dataset_id)


@router.delete("/{dataset_id}", status_code=204)
def delete_dataset(dataset_id: str, db: Session = Depends(get_db)):
    """Delete a dataset and its file."""
    dataset_service.delete_dataset(db, dataset_id)
