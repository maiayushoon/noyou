"""Where the trained model artifacts live on disk."""
from __future__ import annotations

from pathlib import Path

from ..core.config import settings


def model_dir() -> Path:
    """Resolve the model directory (config override, else the package models/ dir)."""
    override = (settings.ml_model_dir or "").strip()
    return Path(override) if override else Path(__file__).resolve().parent / "models"


def model_file() -> Path:
    return model_dir() / "sentiment.joblib"


def meta_file() -> Path:
    return model_dir() / "sentiment.meta.json"
