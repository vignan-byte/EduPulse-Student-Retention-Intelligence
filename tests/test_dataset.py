import pandas as pd
import pytest

from src.ml import load_data


def test_missing_target_rejected(tmp_path):
    path = tmp_path / "bad.csv"
    pd.DataFrame({"Feature": [1]}).to_csv(path, index=False)
    with pytest.raises(ValueError, match="Target"):
        load_data(path)


def test_missing_outcome_rejected(tmp_path):
    path = tmp_path / "bad.csv"
    pd.DataFrame({"Target": ["Dropout", None]}).to_csv(path, index=False)
    with pytest.raises(ValueError, match="target labels"):
        load_data(path)


def test_unknown_outcome_rejected(tmp_path):
    path = tmp_path / "bad.csv"
    pd.DataFrame({"Target": ["Unknown"]}).to_csv(path, index=False)
    with pytest.raises(ValueError, match="target labels"):
        load_data(path)
