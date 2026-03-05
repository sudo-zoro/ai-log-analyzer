"""
Dataset management service.

Handles CSV upload, validation, metadata extraction, and storage.
"""
import os
import uuid
import shutil
import pandas as pd
from pathlib import Path
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from app.models.dataset import Dataset
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

ALLOWED_CONTENT_TYPES = {"text/csv", "application/csv", "application/octet-stream"}
MAX_FILE_SIZE_MB = 100


def save_uploaded_file(upload_file: UploadFile, dest_dir: str) -> tuple[str, int]:
    """Save a raw upload to disk. Returns (file_path, size_bytes)."""
    Path(dest_dir).mkdir(parents=True, exist_ok=True)
    ext = Path(upload_file.filename or "upload.csv").suffix or ".csv"
    file_id = str(uuid.uuid4())
    file_path = str(Path(dest_dir) / f"{file_id}{ext}")

    size = 0
    with open(file_path, "wb") as f:
        while chunk := upload_file.file.read(1024 * 1024):  # 1 MB chunks
            if (size + len(chunk)) > MAX_FILE_SIZE_MB * 1024 * 1024:
                os.remove(file_path)
                raise HTTPException(status_code=413, detail=f"File exceeds {MAX_FILE_SIZE_MB} MB limit.")
            f.write(chunk)
            size += len(chunk)
    return file_path, size


def validate_csv(file_path: str) -> tuple[int, int]:
    """Validate CSV and return (row_count, col_count)."""
    try:
        df = pd.read_csv(file_path, nrows=5)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Invalid CSV: {str(e)}")

    if df.empty:
        raise HTTPException(status_code=422, detail="CSV file is empty.")

    # Count full rows efficiently
    with open(file_path, "r") as f:
        row_count = sum(1 for _ in f) - 1  # subtract header

    return max(row_count, 0), len(df.columns)


def create_dataset(db: Session, upload_file: UploadFile, name: str) -> Dataset:
    """Full pipeline: upload → validate → persist metadata."""
    file_path, size_bytes = save_uploaded_file(upload_file, settings.UPLOAD_DIR)
    row_count, col_count = validate_csv(file_path)

    dataset = Dataset(
        name=name,
        original_filename=upload_file.filename or "unknown.csv",
        file_path=file_path,
        row_count=row_count,
        column_count=col_count,
        file_size_bytes=size_bytes,
        status="validated",
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)
    logger.info("Dataset %s created: %d rows, %d cols", dataset.id, row_count, col_count)
    return dataset


def list_datasets(db: Session) -> list[Dataset]:
    return db.query(Dataset).order_by(Dataset.created_at.desc()).all()


def get_dataset(db: Session, dataset_id: str) -> Dataset:
    ds = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found.")
    return ds


def delete_dataset(db: Session, dataset_id: str) -> None:
    ds = get_dataset(db, dataset_id)
    try:
        Path(ds.file_path).unlink(missing_ok=True)
    except Exception:
        pass
    db.delete(ds)
    db.commit()
    logger.info("Dataset %s deleted", dataset_id)
