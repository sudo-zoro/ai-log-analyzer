import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Integer, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class MLModel(Base):
    __tablename__ = "ml_models"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    algorithm: Mapped[str] = mapped_column(String(100), default="isolation_forest")
    dataset_id: Mapped[str] = mapped_column(String(36), nullable=True)
    model_path: Mapped[str] = mapped_column(String(512), nullable=True)
    scaler_path: Mapped[str] = mapped_column(String(512), nullable=True)
    feature_columns: Mapped[dict] = mapped_column(JSON, nullable=True)   # list of feature names
    hyperparameters: Mapped[dict] = mapped_column(JSON, nullable=True)   # n_estimators, contamination, etc.
    metrics: Mapped[dict] = mapped_column(JSON, nullable=True)           # training metrics
    status: Mapped[str] = mapped_column(String(50), default="pending")   # pending, training, ready, error
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
