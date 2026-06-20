"""Tests for the trainable reputation model and its analyzer."""
from __future__ import annotations

from app.analysis.base import AnalysisInput
from app.analysis.trained import TrainedModelAnalyzer
from app.ml.dataset import LABELS, load_training_data
from app.ml.train import build_pipeline


def test_seed_dataset_is_balanced_and_labeled():
    texts, labels = load_training_data(None)
    assert len(texts) == len(labels) >= 30
    assert set(labels) == set(LABELS)


def test_pipeline_learns_obvious_sentiment():
    texts, labels = load_training_data(None)
    pipe = build_pipeline()
    pipe.fit(texts, labels)
    assert pipe.predict(["an absolute scam, they stole my money and lied"])[0] == "negative"
    assert pipe.predict(["wonderful, trustworthy team, i highly recommend them"])[0] == "positive"


def test_trained_analyzer_falls_back_when_no_model(tmp_path, monkeypatch):
    # Point the model store at an empty dir → no artifact → behaves like rule-based.
    from app.core.config import settings

    monkeypatch.setattr(settings, "ml_model_dir", str(tmp_path))
    analyzer = TrainedModelAnalyzer()
    assert analyzer.is_trained is False
    result = analyzer.analyze(AnalysisInput(content="they scammed me and lied about everything"))
    # Still returns a valid, usable analysis (from the rule-based fallback).
    assert result.sentiment in LABELS
    assert 0 <= result.risk_level <= 5
