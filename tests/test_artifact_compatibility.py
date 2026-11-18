"""Deployment-time checks for serialized supervised learning artifacts."""
import json
from pathlib import Path

import sklearn
from src.registry import sha256_file, verified_load


def test_model_serialization_version():
    assert sklearn.__version__ == "1.7.2", (
        "EduPulse model was serialized with scikit-learn 1.7.2"
    )


def test_model_artifact_integrity_and_load():
    folder = Path(__file__).resolve().parents[1] / "artifacts"
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    for name in ("model.joblib", "metrics.json"):
        assert (folder / name).is_file()
        assert sha256_file(folder / name) == manifest["files"][name]
    bundle, metrics = verified_load(folder)
    assert hasattr(bundle["model"], "predict_proba")
    assert bundle["classes"] == metrics["classes"]
