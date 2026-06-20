"""Train and persist the reputation sentiment model.

Run directly to (re)train on the seed plus everything in the database::

    python -m app.ml.train

The model is a TF-IDF + logistic-regression pipeline — tiny, fast, CPU-only, and
fully offline. It is saved to :func:`app.ml.store.model_file` and loaded by the
``trained`` analyzer. Retrain any time; accuracy improves as labelled data grows.
"""
from __future__ import annotations

import json
from collections import Counter

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from .dataset import LABELS, load_training_data
from .store import meta_file, model_dir, model_file

MODEL_VERSION = 1


def build_pipeline() -> Pipeline:
    """The model architecture. Word + char n-grams over sublinear TF capture short
    reputation phrases, their morphology (great/greatly), and misspellings. A
    ``FeatureUnion`` of word and character features generalises better on the kind of
    terse, noisy text seen in reviews and social posts, while staying CPU-only and fast.
    """
    from sklearn.pipeline import FeatureUnion

    features = FeatureUnion(
        [
            # Word-level: unigrams + bigrams over the curated phrasing.
            (
                "word",
                TfidfVectorizer(
                    analyzer="word",
                    ngram_range=(1, 2),
                    min_df=1,
                    sublinear_tf=True,
                    stop_words="english",
                    strip_accents="unicode",
                    lowercase=True,
                ),
            ),
            # Char-level (within word boundaries): robust to suffixes and typos
            # (scam/scammed/scammer all share strong negative character n-grams).
            (
                "char",
                TfidfVectorizer(
                    analyzer="char_wb",
                    ngram_range=(3, 5),
                    min_df=2,
                    sublinear_tf=True,
                    strip_accents="unicode",
                    lowercase=True,
                ),
            ),
        ]
    )
    return Pipeline(
        [
            ("tfidf", features),
            (
                "clf",
                LogisticRegression(
                    max_iter=2000,
                    C=8.0,
                    class_weight="balanced",
                ),
            ),
        ]
    )


def train(db=None, *, test_size: float = 0.2) -> dict:
    """Fit the pipeline, persist it, and return a metrics summary."""
    import joblib  # local import keeps app startup light

    texts, labels = load_training_data(db)
    counts = Counter(labels)

    pipe = build_pipeline()

    # Hold out a test split only when every class has enough rows to stratify.
    accuracy: float | None = None
    if len(texts) >= 15 and min(counts.values()) >= 2:
        X_train, X_test, y_train, y_test = train_test_split(
            texts, labels, test_size=test_size, random_state=42, stratify=labels
        )
        pipe.fit(X_train, y_train)
        accuracy = round(float(accuracy_score(y_test, pipe.predict(X_test))), 3)

    # Always fit the final model on ALL data so we ship the strongest version.
    pipe.fit(texts, labels)

    out_dir = model_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipe, model_file())

    meta = {
        "version": MODEL_VERSION,
        "algorithm": "tfidf+logreg",
        "n_samples": len(texts),
        "class_counts": dict(counts),
        "classes": sorted(set(labels)),
        "holdout_accuracy": accuracy,
    }
    meta_file().write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return meta


def main() -> None:
    # Open a DB session so real, labelled mentions feed the model.
    try:
        from ..core.database import SessionLocal

        db = SessionLocal()
    except Exception:
        db = None
    try:
        meta = train(db)
    finally:
        if db is not None:
            db.close()

    print("Trained reputation model")
    print(f"  samples   : {meta['n_samples']}")
    print(f"  classes   : {meta['classes']} ({meta['class_counts']})")
    print(f"  accuracy  : {meta['holdout_accuracy']}")
    print(f"  saved to  : {model_file()}")
    # Cheap sanity check on obvious inputs.
    import joblib

    pipe = joblib.load(model_file())
    for sample in ("they scammed me and lied about everything", "wonderful and trustworthy, highly recommend"):
        print(f"  predict({sample!r:55}) -> {pipe.predict([sample])[0]}")


if __name__ == "__main__":
    main()
