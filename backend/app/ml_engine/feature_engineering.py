"""
Feature Engineering Pipeline for Security Logs.

Transforms raw CSV log data into numerical feature vectors
suitable for anomaly detection with Isolation Forest.
"""
import pandas as pd
import numpy as np
from typing import Optional
from app.core.logging import get_logger

logger = get_logger(__name__)


# ─── Numeric coercion helpers ─────────────────────────────────────────────────

def safe_to_numeric(series: pd.Series) -> pd.Series:
    """Try to coerce a series to numeric, fill NaN with 0."""
    return pd.to_numeric(series, errors="coerce").fillna(0)


def encode_categorical(series: pd.Series, top_n: int = 20) -> pd.DataFrame:
    """Label-frequency-encode a categorical column."""
    freq_map = series.value_counts(normalize=True).head(top_n).to_dict()
    encoded = series.map(freq_map).fillna(0.0)
    return encoded.rename(series.name + "_freq")


# ─── Common log-field detectors ───────────────────────────────────────────────

HTTP_METHODS = {"GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"}
COMMON_NUMERIC_HINTS = [
    "status", "code", "duration", "time", "latency", "size",
    "bytes", "count", "length", "port", "score", "flag", "level",
]
COMMON_CATEGORICAL_HINTS = [
    "method", "protocol", "type", "action", "category", "label",
    "source", "dest", "host", "user", "agent", "country",
]


def classify_columns(df: pd.DataFrame):
    """
    Classify dataframe columns into numeric vs categorical groups
    using column names and dtype heuristics.
    """
    numeric_cols = []
    categorical_cols = []

    for col in df.columns:
        col_lower = col.lower()

        if df[col].dtype in [np.float64, np.int64, np.float32, np.int32]:
            numeric_cols.append(col)
        elif df[col].dtype == object:
            # Try numeric conversion first
            converted = pd.to_numeric(df[col], errors="coerce")
            if converted.notna().mean() > 0.8:
                numeric_cols.append(col)
            elif any(hint in col_lower for hint in COMMON_CATEGORICAL_HINTS):
                categorical_cols.append(col)
            elif df[col].nunique() < 50:
                categorical_cols.append(col)
            else:
                # High-cardinality text – skip for now
                pass

    return numeric_cols, categorical_cols


# ─── Main feature engineering function ───────────────────────────────────────

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build a numeric feature matrix from a raw log DataFrame.
    Returns a new DataFrame with all-numeric columns ready for ML.
    """
    logger.info("Engineering features for %d rows, %d columns", len(df), len(df.columns))

    feature_parts = []
    numeric_cols, categorical_cols = classify_columns(df)

    # 1. Numeric columns → coerce and fill
    if numeric_cols:
        num_df = df[numeric_cols].apply(safe_to_numeric)
        feature_parts.append(num_df)
        logger.info("Numeric columns (%d): %s", len(numeric_cols), numeric_cols)

    # 2. Categorical columns → frequency encoding
    if categorical_cols:
        for col in categorical_cols:
            encoded = encode_categorical(df[col])
            feature_parts.append(encoded)
        logger.info("Categorical columns (%d): %s", len(categorical_cols), categorical_cols)

    if not feature_parts:
        raise ValueError("No usable features found in dataset. Ensure CSV has numeric or categorical columns.")

    feature_df = pd.concat(feature_parts, axis=1)
    feature_df = feature_df.fillna(0)

    logger.info("Feature matrix shape: %s", feature_df.shape)
    return feature_df


def get_feature_columns(df: pd.DataFrame) -> list[str]:
    """Return the list of feature column names that would be generated."""
    return list(engineer_features(df).columns)
