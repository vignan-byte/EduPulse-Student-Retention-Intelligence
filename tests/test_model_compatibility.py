"""Regression tests for model compatibility and SimpleImputer cross-version stability."""
import numpy as np
import pandas as pd
import pytest

from src.registry import verified_load, ensure_imputer_compatibility
from src.ml import load_data, stage_features, predict_student
from src.intelligence import get_preset_student_profiles
from src.explain import explain_shap


@pytest.fixture(scope="module")
def artifacts():
    bundle, metrics = verified_load("artifacts")
    return bundle, metrics


def test_simple_imputer_compatibility_patch(artifacts):
    bundle, _ = artifacts
    # Artificially delete fill_dtype or _fit_dtype on an imputer to simulate version discrepancy
    for cc in bundle["model"].calibrated_classifiers_:
        est = getattr(cc, "estimator", getattr(cc, "base_estimator", None))
        ct = est.named_steps["preprocess"]
        for tname, trans, cols in ct.transformers_:
            if hasattr(trans, "named_steps") and "impute" in trans.named_steps:
                imp = trans.named_steps["impute"]
                if hasattr(imp, "fill_dtype"):
                    delattr(imp, "fill_dtype")
                assert not hasattr(imp, "fill_dtype")

    # Run patching hook
    ensure_imputer_compatibility(bundle["model"])

    # Verify both attributes are now restored and consistent
    for cc in bundle["model"].calibrated_classifiers_:
        est = getattr(cc, "estimator", getattr(cc, "base_estimator", None))
        ct = est.named_steps["preprocess"]
        for tname, trans, cols in ct.transformers_:
            if hasattr(trans, "named_steps") and "impute" in trans.named_steps:
                imp = trans.named_steps["impute"]
                assert hasattr(imp, "fill_dtype")
                assert hasattr(imp, "_fit_dtype")
                assert imp.fill_dtype == imp._fit_dtype


def test_student_index_130_inference(artifacts):
    """Explicit regression test for student index 130 inference."""
    bundle, metrics = artifacts
    df = load_data("data/students.csv")
    assert len(df) > 130
    row130 = df.iloc[[130]]
    feat130 = stage_features(row130, bundle["stage"])
    
    preds = predict_student(bundle, feat130)
    assert len(preds) == 3
    probs = preds["probability"].values
    assert np.all(np.isfinite(probs))
    assert np.isclose(np.sum(probs), 1.0, atol=1e-4)
    assert set(preds["outcome"]) == set(bundle["classes"])


def test_all_demo_personas_inference(artifacts):
    """Verify all 3 demonstration personas produce valid model predictions."""
    bundle, _ = artifacts
    presets = get_preset_student_profiles()
    assert len(presets) >= 3

    for persona_name, profile_dict in presets.items():
        base_df = pd.DataFrame([profile_dict])
        eval_df = base_df.copy()
        for c in set(bundle["features"]) - set(eval_df.columns):
            eval_df[c] = 0.0
        
        preds = predict_student(bundle, eval_df[bundle["features"]])
        assert len(preds) == 3
        probs = preds["probability"].values
        assert np.all(np.isfinite(probs))
        assert np.isclose(np.sum(probs), 1.0, atol=1e-4)


def test_student_index_130_shap_explanation(artifacts):
    """Verify SHAP explanation generation runs without SimpleImputer errors."""
    bundle, _ = artifacts
    df = load_data("data/students.csv")
    background = stage_features(df.head(20), bundle["stage"])[bundle["features"]]
    row130 = stage_features(df.iloc[[130]], bundle["stage"])[bundle["features"]]

    shap_df = explain_shap(bundle["model"], background, row130)
    assert len(shap_df) > 0
    assert "feature" in shap_df.columns
    assert "shap_effect" in shap_df.columns
    assert np.all(np.isfinite(shap_df["shap_effect"]))
    assert "additivity_error" in shap_df.attrs
