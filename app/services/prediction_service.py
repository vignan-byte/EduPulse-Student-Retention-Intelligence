"""Prediction Service: handles single student evaluation and cohort screening."""
from __future__ import annotations
import numpy as np
import pandas as pd
from app.services.model_service import get_bundle, get_metrics, get_raw_data
from src.intelligence import recommendations, screen_cohort


def prepare_student_record(data: dict | pd.Series | pd.DataFrame) -> pd.DataFrame:
    bundle = get_bundle()
    features = bundle["features"]
    raw_data = get_raw_data()
    
    if isinstance(data, pd.DataFrame):
        df = data.copy()
    elif isinstance(data, pd.Series):
        df = pd.DataFrame([data])
    elif isinstance(data, dict):
        df = pd.DataFrame([data])
    else:
        raise ValueError("Data must be dict, Series, or DataFrame")
        
    # Impute missing feature columns using median of reference data
    for feat in features:
        if feat not in df.columns:
            if feat in raw_data.columns and pd.api.types.is_numeric_dtype(raw_data[feat]):
                df[feat] = raw_data[feat].median()
            else:
                df[feat] = 0.0
        else:
            df[feat] = pd.to_numeric(df[feat], errors="coerce").fillna(0.0)
            
    return df[features]


def predict_single(data: dict | pd.Series | pd.DataFrame, threshold: float | None = None) -> dict:
    bundle = get_bundle()
    metrics = get_metrics()
    
    if threshold is None:
        threshold = float(metrics.get("selected_screening_threshold", 0.38))
    else:
        threshold = float(threshold)
        
    record = prepare_student_record(data)
    model = bundle["model"]
    classes = list(model.classes_)
    
    probabilities = model.predict_proba(record)[0]
    prob_dict = {classes[i]: round(float(probabilities[i]), 4) for i in range(len(classes))}
    
    dropout_idx = classes.index("Dropout")
    dropout_prob = float(probabilities[dropout_idx])
    
    top_idx = int(np.argmax(probabilities))
    top_class = classes[top_idx]
    top_conf = float(probabilities[top_idx])
    
    # Priority decision
    if dropout_prob >= threshold:
        priority = "Advisor review"
        risk_tier = "High Risk"
        badge_color = "danger"
    elif dropout_prob >= 0.30:
        priority = "Moderate watch"
        risk_tier = "Moderate Risk"
        badge_color = "warning"
    else:
        priority = "Routine support"
        risk_tier = "Low Risk"
        badge_color = "success"
        
    is_screened = bool(dropout_prob >= threshold)
    is_uncertain = bool(top_conf < 0.60)
    
    # Generate transparent evidence-linked recommendations
    recs_df = recommendations(record)
    recs_list = recs_df.to_dict(orient="records")
    
    return {
        "status": "success",
        "probabilities": prob_dict,
        "dropout_probability": round(dropout_prob, 4),
        "screening_threshold": threshold,
        "is_screened": is_screened,
        "risk_tier": risk_tier,
        "review_priority": priority,
        "badge_color": badge_color,
        "top_predicted_outcome": top_class,
        "top_class_confidence": round(top_conf, 4),
        "uncertain_prediction": is_uncertain,
        "recommendations": recs_list,
        "features": {k: float(record[k].iloc[0]) for k in record.columns}
    }


def predict_cohort_batch(file_or_df, threshold: float | None = None) -> dict:
    bundle = get_bundle()
    metrics = get_metrics()
    
    if threshold is None:
        threshold = float(metrics.get("selected_screening_threshold", 0.38))
    else:
        threshold = float(threshold)
        
    if isinstance(file_or_df, pd.DataFrame):
        df = file_or_df.copy()
    else:
        df = pd.read_csv(file_or_df)
        
    # Check features
    features = bundle["features"]
    raw_data = get_raw_data()
    for feat in features:
        if feat not in df.columns:
            if feat in raw_data.columns:
                df[feat] = raw_data[feat].median()
            else:
                df[feat] = 0.0
        else:
            df[feat] = pd.to_numeric(df[feat], errors="coerce").fillna(0.0)
            
    screening_df = screen_cohort(bundle, {"selected_screening_threshold": threshold}, df)
    
    total = len(screening_df)
    flagged = int((screening_df["dropout_probability"] >= threshold).sum())
    moderate = int(((screening_df["dropout_probability"] >= 0.30) & (screening_df["dropout_probability"] < threshold)).sum())
    routine = total - flagged - moderate
    avg_risk = float(screening_df["dropout_probability"].mean())
    
    # Top 50 highest risk records for display table
    high_risk_records = screening_df.sort_values("dropout_probability", ascending=False).head(50).to_dict(orient="records")
    
    return {
        "total_records": total,
        "screening_threshold": threshold,
        "flagged_count": flagged,
        "flagged_percentage": round((flagged / total) * 100, 1) if total > 0 else 0,
        "moderate_count": moderate,
        "routine_count": routine,
        "average_risk": round(avg_risk, 4),
        "results_sample": high_risk_records
    }
