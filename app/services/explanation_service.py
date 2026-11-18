"""Explanation Service: SHAP and LIME Explainable AI workflows."""
from __future__ import annotations
import json
import hashlib
import numpy as np
import pandas as pd
from app.services.model_service import get_bundle, get_raw_data
from app.services.prediction_service import prepare_student_record
from src.explain import explain_shap, explain_lime, plot_shap_figure, plot_lime_figure

_SHAP_CACHE: dict[str, dict] = {}
_LIME_CACHE: dict[str, dict] = {}


def _record_key(record: pd.DataFrame) -> str:
    s = json.dumps(record.to_dict(orient="records")[0], sort_keys=True)
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def compute_shap(data: dict | pd.DataFrame, max_background: int = 25, top_n: int = 12) -> dict:
    bundle = get_bundle()
    raw_df = get_raw_data()
    record = prepare_student_record(data)
    
    key = f"{_record_key(record)}_{max_background}_{top_n}"
    if key in _SHAP_CACHE:
        return _SHAP_CACHE[key]
        
    shap_df = explain_shap(
        model=bundle["model"],
        background=raw_df[bundle["features"]],
        record=record,
        max_background=max_background
    )
    
    fig = plot_shap_figure(shap_df, top_n=top_n)
    
    # Extract top features for UI cards/tables
    top_records = []
    for _, row in shap_df.head(top_n).iterrows():
        val = float(row["shap_effect"])
        feat = str(row["feature"])
        student_val = float(record[feat].iloc[0]) if feat in record.columns else 0.0
        top_records.append({
            "feature": feat,
            "shap_effect": round(val, 4),
            "student_value": round(student_val, 2),
            "direction": "risk_driver" if val > 0 else "protective",
            "interpretation": f"Increases dropout probability by {abs(val):.3f}" if val > 0 else f"Protective: lowers dropout probability by {abs(val):.3f}"
        })
        
    result = {
        "status": "success",
        "top_features": top_records,
        "base_prediction": round(float(shap_df.attrs.get("prediction", 0.0)), 4),
        "additivity_error": float(shap_df.attrs.get("additivity_error", 0.0)),
        "plotly_json": json.loads(fig.to_json())
    }
    
    _SHAP_CACHE[key] = result
    return result


def compute_lime(data: dict | pd.DataFrame, top_n: int = 10) -> dict:
    bundle = get_bundle()
    raw_df = get_raw_data()
    record = prepare_student_record(data)
    
    key = f"{_record_key(record)}_{top_n}"
    if key in _LIME_CACHE:
        return _LIME_CACHE[key]
        
    lime_df = explain_lime(
        model=bundle["model"],
        background=raw_df[bundle["features"]],
        record=record
    )
    
    fig = plot_lime_figure(lime_df, top_n=top_n)
    
    top_records = []
    for _, row in lime_df.head(top_n).iterrows():
        val = float(row["lime_weight"])
        cond = str(row["condition"])
        top_records.append({
            "condition": cond,
            "lime_weight": round(val, 4),
            "direction": "risk_driver" if val > 0 else "protective",
            "interpretation": f"Local surrogate rule elevates dropout odds" if val > 0 else f"Local surrogate rule supports retention"
        })
        
    result = {
        "status": "success",
        "rules": top_records,
        "plotly_json": json.loads(fig.to_json())
    }
    
    _LIME_CACHE[key] = result
    return result
