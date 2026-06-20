"""Trainable, offline reputation model.

A free, no-GPU, no-API-key sentiment model (TF-IDF + linear classifier) that NoYou
owns and can retrain as real labelled data accumulates. Train it with::

    python -m app.ml.train

Activate it with ``ANALYZER=trained``. Until a model is trained, the analyzer
degrades to the rule-based engine, so nothing breaks.
"""
