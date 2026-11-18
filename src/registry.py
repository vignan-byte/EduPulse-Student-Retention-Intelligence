"""Local model artifact integrity checks (not a substitute for signing/auth)."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import joblib


def sha256_file(path: str | Path) -> str:
    p = Path(path)
    # Normalize CRLF to LF for text/JSON files to ensure deterministic cross-platform hashing
    if p.suffix in (".json", ".txt", ".csv", ".md"):
        content = p.read_bytes().replace(b"\r\n", b"\n")
        return hashlib.sha256(content).hexdigest()
    digest = hashlib.sha256()
    with open(p, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_manifest(folder: str | Path, version: str = "9.0.0") -> dict:
    folder = Path(folder)
    files = ["model.joblib", "metrics.json"]
    manifest = {"release_version": version,
                "files": {name: sha256_file(folder / name) for name in files}}
    (folder / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def ensure_imputer_compatibility(obj) -> None:
    """Recursively patches SimpleImputer instances to ensure both _fit_dtype and fill_dtype exist.
    
    Protects against AttributeError: 'SimpleImputer' object has no attribute 'fill_dtype'
    across differing scikit-learn serialization environments.
    """
    if obj is None:
        return
    if "SimpleImputer" in type(obj).__name__:
        import numpy as np
        fit_dt = getattr(obj, "_fit_dtype", None)
        fill_dt = getattr(obj, "fill_dtype", None)
        target_dtype = fit_dt if fit_dt is not None else (fill_dt if fill_dt is not None else np.dtype("float64"))
        obj._fit_dtype = target_dtype
        obj.fill_dtype = target_dtype
        return
    if hasattr(obj, "calibrated_classifiers_"):
        for cc in obj.calibrated_classifiers_:
            base = getattr(cc, "estimator", getattr(cc, "base_estimator", None))
            ensure_imputer_compatibility(base)
    if hasattr(obj, "estimator"):
        ensure_imputer_compatibility(getattr(obj, "estimator"))
    if hasattr(obj, "base_estimator"):
        ensure_imputer_compatibility(getattr(obj, "base_estimator"))
    if hasattr(obj, "steps"):
        for _, step in obj.steps:
            ensure_imputer_compatibility(step)
    if hasattr(obj, "named_steps"):
        for _, step in obj.named_steps.items():
            ensure_imputer_compatibility(step)
    if hasattr(obj, "transformers_"):
        for item in obj.transformers_:
            if len(item) >= 2:
                ensure_imputer_compatibility(item[1])
    if hasattr(obj, "transformers"):
        for item in obj.transformers:
            if len(item) >= 2:
                ensure_imputer_compatibility(item[1])


def verified_load(folder: str | Path) -> tuple[dict, dict]:
    """Reject changed/missing artifacts before deserializing a trusted local joblib."""
    folder = Path(folder)
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    for name in ("model.joblib", "metrics.json"):
        if manifest.get("files", {}).get(name) != sha256_file(folder / name):
            raise ValueError(f"Model artifact integrity check failed: {name}")
    # A hash in the same folder is not an authenticity guarantee. Never load
    # a model from an untrusted publisher even when this check passes.
    bundle = joblib.load(folder / "model.joblib")
    metrics = json.loads((folder / "metrics.json").read_text(encoding="utf-8"))
    if bundle["classes"] != metrics["classes"] or bundle["stage"] != metrics["stage"]:
        raise ValueError("Model and metrics metadata disagree")
    
    # Guarantee cross-version scikit-learn imputer compatibility
    ensure_imputer_compatibility(bundle.get("model"))
    
    return bundle, metrics
