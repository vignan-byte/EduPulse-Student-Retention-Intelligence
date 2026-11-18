import pandas as pd
import pytest

from src.ml import (make_pipeline, predict_student, stage_features, dropout_diagnostics,
                    subgroup_diagnostics, choose_screening_threshold)


def test_stage_removes_future_semesters():
    df = pd.DataFrame({"Age at enrollment": [20], "Curricular units 1st sem (grade)": [12],
                       "Curricular units 2nd sem (grade)": [10], "Target": ["Dropout"]})
    assert list(stage_features(df, "Admission")) == ["Age at enrollment"]
    assert list(stage_features(df, "After semester 1")) == ["Age at enrollment", "Curricular units 1st sem (grade)"]
    assert len(stage_features(df, "After semester 2").columns) == 3


def test_invalid_stage_and_model():
    with pytest.raises(ValueError):
        stage_features(pd.DataFrame(), "tomorrow")
    with pytest.raises(ValueError):
        make_pipeline(pd.DataFrame({"x": [1]}), "unknown")


def test_missing_prediction_features_rejected():
    with pytest.raises(ValueError, match="Missing model features"):
        predict_student({"features": ["a", "b"]}, pd.DataFrame({"a": [1]}))


def test_screening_confusion_counts_and_calibration():
    import numpy as np
    y = ["Dropout", "Graduate", "Dropout", "Enrolled"]
    p = np.array([[.8, .1, .1], [.7, .1, .2], [.2, .3, .5], [.1, .6, .3]])
    result = dropout_diagnostics(y, p, ["Dropout", "Enrolled", "Graduate"])
    assert (result["tp"], result["fn"], result["fp"], result["tn"]) == (1, 1, 1, 1)
    assert result["precision"] == .5
    assert result["recall"] == .5
    assert 0 <= result["expected_calibration_error_10bin"] <= 1


def test_subgroup_small_groups_suppressed():
    import numpy as np
    X = pd.DataFrame({"Gender": [0, 0, 1, 1]})
    result = subgroup_diagnostics(X, ["Dropout", "Graduate", "Enrolled", "Dropout"],
                                  np.array([[.8, .1, .1]] * 4), ["Dropout", "Enrolled", "Graduate"],
                                  "Gender", min_group=3)
    assert result == []


def test_subgroup_reports_rates_only_for_sufficient_class_counts():
    import numpy as np
    X = pd.DataFrame({"Gender": [0] * 40 + [1] * 40})
    y = ["Dropout"] * 20 + ["Graduate"] * 20 + ["Dropout"] * 5 + ["Graduate"] * 35
    prob = np.tile([[.6, .2, .2]], (80, 1))
    result = subgroup_diagnostics(X, y, prob, ["Dropout", "Enrolled", "Graduate"], "Gender")
    assert len(result) == 1
    assert result[0]["dropout_count"] == 20
    assert result[0]["false_positive_rate"] == 1.0


def test_screening_threshold_chosen_from_scores():
    chosen, info = choose_screening_threshold(
        ["Dropout", "Dropout", "Graduate", "Enrolled"], [.9, .8, .2, .1], .8)
    assert .2 < chosen <= .8
    assert info["met_precision_target"]
    assert info["oof_recall"] == 1.0


def test_invalid_threshold_inputs_rejected():
    with pytest.raises(ValueError):
        choose_screening_threshold(["Dropout"], [float("nan")])
