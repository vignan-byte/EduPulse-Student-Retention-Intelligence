"""Model Service: handles access to ML artifacts, benchmark metrics, and student data."""
from __future__ import annotations
import numpy as np
import pandas as pd
from app.extensions import model_manager
from src.intelligence import get_preset_student_profiles


def get_bundle() -> dict:
    if not model_manager.is_loaded or model_manager.bundle is None:
        raise RuntimeError("Model bundle has not been initialized.")
    return model_manager.bundle


def get_metrics() -> dict:
    if not model_manager.is_loaded or model_manager.metrics is None:
        raise RuntimeError("Model metrics have not been initialized.")
    return model_manager.metrics


def get_raw_data() -> pd.DataFrame:
    if not model_manager.is_loaded or model_manager.df_raw is None:
        raise RuntimeError("Reference dataset has not been initialized.")
    return model_manager.df_raw


def get_case_store():
    if not model_manager.is_loaded or model_manager.case_store is None:
        raise RuntimeError("Case store has not been initialized.")
    return model_manager.case_store


def get_feature_names() -> list[str]:
    return list(get_bundle()["features"])


def get_classes() -> list[str]:
    return list(get_bundle()["model"].classes_)


def get_archetypes() -> dict[str, dict]:
    return get_preset_student_profiles()


def get_student_by_index(idx: int) -> dict:
    df = get_raw_data()
    if idx < 0 or idx >= len(df):
        raise IndexError(f"Student index {idx} out of range (0-{len(df)-1})")
    row = df.iloc[idx].to_dict()
    # Format floats for clean JSON
    clean_row = {}
    for k, v in row.items():
        if isinstance(v, (np.floating, float)):
            clean_row[k] = float(v)
        elif isinstance(v, (np.integer, int)):
            clean_row[k] = int(v)
        else:
            clean_row[k] = str(v)
    return clean_row


def get_overview_statistics() -> dict:
    df = get_raw_data()
    metrics = get_metrics()
    bundle = get_bundle()
    
    target_counts = df["Target"].value_counts().to_dict()
    total_students = len(df)
    
    target_dist = {
        k: {
            "count": int(v),
            "percentage": round((v / total_students) * 100, 2)
        }
        for k, v in target_counts.items()
    }
    
    # Financial indicators
    debtor_count = int(df["Debtor"].sum()) if "Debtor" in df.columns else 0
    scholarship_count = int(df["Scholarship holder"].sum()) if "Scholarship holder" in df.columns else 0
    
    # Academic performance averages
    avg_admission = float(df["Admission grade"].mean()) if "Admission grade" in df.columns else 0.0
    avg_sem1_grade = float(df["Curricular units 1st sem (grade)"].mean()) if "Curricular units 1st sem (grade)" in df.columns else 0.0
    
    enrolled_s1 = df["Curricular units 1st sem (enrolled)"].replace(0, np.nan)
    approved_s1 = df["Curricular units 1st sem (approved)"]
    avg_completion_ratio = float((approved_s1 / enrolled_s1).dropna().mean() * 100)
    
    return {
        "total_students": total_students,
        "feature_count": len(bundle["features"]),
        "selected_model": metrics.get("selected_model", "Calibrated Classifier"),
        "test_accuracy": round(float(metrics.get("test_accuracy", 0.0)) * 100, 2),
        "test_macro_f1": round(float(metrics.get("test_macro_f1", 0.0)) * 100, 2),
        "screening_threshold": float(metrics.get("selected_screening_threshold", 0.38)),
        "target_distribution": target_dist,
        "debtor_rate": round((debtor_count / total_students) * 100, 1),
        "scholarship_rate": round((scholarship_count / total_students) * 100, 1),
        "avg_admission_grade": round(avg_admission, 1),
        "avg_sem1_grade": round(avg_sem1_grade, 2),
        "avg_completion_ratio": round(avg_completion_ratio, 1),
    }
