import json
from pathlib import Path

import pytest

from src.registry import sha256_file, write_manifest, verified_load


def test_manifest_changes_detected_before_joblib_deserialization(tmp_path):
    (tmp_path / "model.joblib").write_bytes(b"not a model")
    (tmp_path / "metrics.json").write_text("{}")
    manifest = write_manifest(tmp_path)
    assert len(manifest["files"]["model.joblib"]) == 64
    (tmp_path / "model.joblib").write_bytes(b"tampered")
    with pytest.raises(ValueError, match="integrity"):
        verified_load(tmp_path)


def test_missing_model_rejected(tmp_path):
    (tmp_path / "metrics.json").write_text("{}")
    with pytest.raises(FileNotFoundError):
        write_manifest(tmp_path)
