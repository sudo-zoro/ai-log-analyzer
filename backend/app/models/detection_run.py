import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Integer, Text, JSON, Float
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class DetectionRun(Base):
    __tablename__ = "detection_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    model_id: Mapped[str] = mapped_column(String(36), nullable=False)
    input_file: Mapped[str] = mapped_column(String(512), nullable=True)
    total_rows: Mapped[int] = mapped_column(Integer, nullable=True)
    anomaly_count: Mapped[int] = mapped_column(Integer, nullable=True)
    anomaly_ratio: Mapped[float] = mapped_column(Float, nullable=True)
    results: Mapped[dict] = mapped_column(JSON, nullable=True)   # anomaly indices + scores
    status: Mapped[str] = mapped_column(String(50), default="pending")  # pending, running, done, error
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
