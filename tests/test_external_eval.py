import numpy as np
import pandas as pd
import pytest

from src.external_eval import bootstrap_macro_f1_interval, evaluate_cohort


class DummyModel:
    classes_ = np.array(["Dropout", "Enrolled", "Graduate"])
    def predict(self, X):
        return np.array(["Dropout"] * len(X))
    def predict_proba(self, X):
        return np.tile([.8, .1, .1], (len(X), 1))


def test_bootstrap_interval_is_deterministic():
    y = ["Dropout", "Graduate"] * 15
    p = ["Dropout", "Graduate"] * 15
    assert bootstrap_macro_f1_interval(y, p, 100, 3) == bootstrap_macro_f1_interval(y, p, 100, 3)


def test_external_eval_rejects_unlabeled_data():
    bundle = {"features": ["x"], "model": DummyModel(), "stage": "Admission"}
    with pytest.raises(ValueError, match="Target"):
        evaluate_cohort(bundle, {}, pd.DataFrame({"x": [1]*30}))


def test_external_eval_measures_labeled_cohort():
    bundle = {"features": ["x"], "model": DummyModel(), "stage": "Admission"}
    frame = pd.DataFrame({"x": range(30), "Target": ["Dropout"] * 15 + ["Graduate"] * 15})
    report = evaluate_cohort(bundle, {"selected_screening_threshold": .5}, frame)
    assert report["rows"] == 30
    assert report["dropout_screening"]["tp"] == 15
    assert report["dropout_screening"]["fp"] == 15
