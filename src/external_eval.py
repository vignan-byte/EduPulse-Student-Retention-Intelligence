"""Evaluate a trusted model on a genuinely independent labeled cohort."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, log_loss

from .ml import OUTCOMES, TARGET, dropout_diagnostics
from .registry import verified_load


def bootstrap_macro_f1_interval(y_true, predictions, samples=1000, seed=42):
    """Percentile bootstrap CI; descriptive, not correction for dataset shift."""
    actual, pred = np.asarray(y_true), np.asarray(predictions)
    if len(actual) != len(pred) or len(actual) < 20 or samples < 100:
        raise ValueError("Need matching samples, 20+ records, and 100+ bootstrap samples")
    rng = np.random.default_rng(seed)
    scores = []
    for _ in range(samples):
        indices = rng.integers(0, len(actual), len(actual))
        scores.append(f1_score(actual[indices], pred[indices], labels=OUTCOMES,
                               average="macro", zero_division=0))
    return [float(x) for x in np.quantile(scores, [0.025, 0.975])]


def evaluate_cohort(bundle: dict, metrics: dict, cohort: pd.DataFrame):
    if TARGET not in cohort:
        raise ValueError("Labeled cohort must contain Target")
    if len(cohort) < 30 or cohort[TARGET].isna().any():
        raise ValueError("Need 30+ labeled and complete outcome records")
    if not set(cohort[TARGET]).issubset(set(OUTCOMES)):
        raise ValueError("Unexpected target classes")
    required = bundle["features"]
    missing = set(required) - set(cohort.columns)
    if missing:
        raise ValueError(f"Missing required model features: {sorted(missing)[:8]}")
    model = bundle["model"]
    X, y = cohort[required], cohort[TARGET].to_numpy()
    prob, pred = model.predict_proba(X), model.predict(X)
    classes = list(model.classes_)
    return {"rows": len(y), "stage": bundle["stage"],
            "accuracy": float(accuracy_score(y, pred)),
            "macro_f1": float(f1_score(y, pred, labels=OUTCOMES, average="macro", zero_division=0)),
            "macro_f1_bootstrap_95pct": bootstrap_macro_f1_interval(y, pred),
            "log_loss": float(log_loss(y, prob, labels=classes)),
            "confusion_matrix": confusion_matrix(y, pred, labels=classes).tolist(),
            "dropout_screening": dropout_diagnostics(y, prob, classes,
                float(metrics["selected_screening_threshold"])),
            "warning": "Only genuinely separate institutional/temporal data can establish transferability. Do not reuse training or test data as external validation."}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-dir", default="artifacts")
    parser.add_argument("--cohort", required=True, help="Approved independent labeled CSV")
    parser.add_argument("--output", default="external_validation.json")
    args = parser.parse_args()
    bundle, metrics = verified_load(args.model_dir)
    report = evaluate_cohort(bundle, metrics, pd.read_csv(args.cohort))
    Path(args.output).write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Evaluated {report['rows']} rows; macro-F1={report['macro_f1']:.3f}")


if __name__ == "__main__":
    main()
