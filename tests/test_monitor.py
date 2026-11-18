import pandas as pd
import pytest

from src.monitor import drift_report


def test_detects_strong_numeric_and_categorical_shift():
    reference = pd.DataFrame({"Age at enrollment": [18] * 50,
                              "Scholarship holder": [0] * 50})
    candidate = pd.DataFrame({"Age at enrollment": [50] * 50,
                              "Scholarship holder": [1] * 50})
    report = drift_report(reference, candidate)
    assert report["flagged_features"] == 2
    assert report["shared_features"] == 2


def test_rejects_tiny_or_incompatible_batches():
    with pytest.raises(ValueError):
        drift_report(pd.DataFrame({"a": [1]}), pd.DataFrame({"a": [2]}))
    with pytest.raises(ValueError, match="shared"):
        drift_report(pd.DataFrame({"a": [1]*30}), pd.DataFrame({"b": [2]*30}))
