"""Offline covariate-shift report for governed, non-identifying feature tables."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import ks_2samp

from .ml import CAT_COLS, TARGET


def calculate_psi(reference: pd.Series, candidate: pd.Series, num_buckets: int = 10) -> float:
    """Calculate Population Stability Index (PSI) between reference and candidate cohorts."""
    ref = pd.to_numeric(reference, errors='coerce').dropna()
    cand = pd.to_numeric(candidate, errors='coerce').dropna()
    if len(ref) < 10 or len(cand) < 10:
        return 0.0
    quantiles = np.linspace(0, 1, num_buckets + 1)
    bins = np.percentile(ref, quantiles * 100)
    bins = np.unique(bins)
    if len(bins) < 2:
        return 0.0
    bins[0] = -np.inf
    bins[-1] = np.inf
    ref_counts, _ = np.histogram(ref, bins=bins)
    cand_counts, _ = np.histogram(cand, bins=bins)
    ref_pct = (ref_counts + 1e-4) / (len(ref) + 1e-4 * len(ref_counts))
    cand_pct = (cand_counts + 1e-4) / (len(cand) + 1e-4 * len(cand_counts))
    return float(np.sum((cand_pct - ref_pct) * np.log(cand_pct / ref_pct)))


def drift_report(reference: pd.DataFrame, candidate: pd.DataFrame, minimum_rows=30) -> dict:
    if len(reference) < minimum_rows or len(candidate) < minimum_rows:
        raise ValueError(f"Need at least {minimum_rows} rows per dataset for exploratory comparison")
    features = [c for c in reference.columns if c != TARGET and c in candidate]
    if not features:
        raise ValueError("No shared feature columns")
    results = []
    for column in features:
        left, right = reference[column], candidate[column]
        missing_shift = abs(float(left.isna().mean()) - float(right.isna().mean()))
        if column in CAT_COLS:
            a = left.astype("string").fillna("<missing>").value_counts(normalize=True)
            b = right.astype("string").fillna("<missing>").value_counts(normalize=True)
            keys = a.index.union(b.index)
            distance = float((a.reindex(keys, fill_value=0) - b.reindex(keys, fill_value=0)).abs().sum() / 2)
            results.append({
                "feature": column, "method": "total_variation", "distance": distance,
                "psi": None,
                "missing_rate_shift": missing_shift, "review": distance >= .2
            })
        else:
            a = pd.to_numeric(left, errors="coerce").dropna()
            b = pd.to_numeric(right, errors="coerce").dropna()
            if len(a) < 10 or len(b) < 10:
                continue
            distance = float(ks_2samp(a, b).statistic)
            psi = calculate_psi(left, right)
            results.append({
                "feature": column, "method": "ks_statistic", "distance": distance,
                "psi": round(psi, 4),
                "missing_rate_shift": missing_shift, "review": distance >= .2 or psi >= 0.25
            })
    return {"reference_rows": len(reference), "candidate_rows": len(candidate),
            "shared_features": len(features), "flagged_features": sum(x["review"] for x in results),
            "features": sorted(results, key=lambda r: r["distance"], reverse=True),
            "warning": "Exploratory covariate shift only; not a validated production drift alarm or fairness audit."}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference", required=True)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--output", default="drift_report.json")
    args = parser.parse_args()
    result = drift_report(pd.read_csv(args.reference), pd.read_csv(args.candidate))
    Path(args.output).write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Wrote {args.output}; flagged {result['flagged_features']} features")


if __name__ == "__main__":
    main()
