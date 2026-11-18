"""Simulation Service: Digital Twin What-If counterfactual scenario modeling."""
from __future__ import annotations
import numpy as np
import pandas as pd
from app.services.model_service import get_bundle, get_metrics
from app.services.prediction_service import prepare_student_record, predict_single
from src.intelligence import counterfactual_recourse


def validate_student_constraints(data: dict) -> list[str]:
    """Validate academic and logical integrity constraints for student features."""
    warnings = []
    
    enrolled_s1 = float(data.get("Curricular units 1st sem (enrolled)", 0))
    approved_s1 = float(data.get("Curricular units 1st sem (approved)", 0))
    grade_s1 = float(data.get("Curricular units 1st sem (grade)", 0))
    
    if approved_s1 > enrolled_s1:
        warnings.append(f"Approved units (1st sem: {approved_s1:g}) cannot exceed enrolled units ({enrolled_s1:g}). Clamped to enrolled.")
        
    if grade_s1 < 0 or grade_s1 > 20:
        warnings.append(f"1st sem grade ({grade_s1:g}) is out of 0–20 standard grading scale.")
        
    enrolled_s2 = float(data.get("Curricular units 2nd sem (enrolled)", 0))
    approved_s2 = float(data.get("Curricular units 2nd sem (approved)", 0))
    grade_s2 = float(data.get("Curricular units 2nd sem (grade)", 0))
    
    if approved_s2 > enrolled_s2 and enrolled_s2 > 0:
        warnings.append(f"Approved units (2nd sem: {approved_s2:g}) cannot exceed enrolled units ({enrolled_s2:g}). Clamped to enrolled.")
        
    if grade_s2 < 0 or grade_s2 > 20:
        warnings.append(f"2nd sem grade ({grade_s2:g}) is out of 0–20 standard grading scale.")
        
    return warnings


def simulate_digital_twin(baseline_dict: dict, modified_dict: dict, threshold: float | None = None) -> dict:
    bundle = get_bundle()
    metrics = get_metrics()
    
    if threshold is None:
        threshold = float(metrics.get("selected_screening_threshold", 0.38))
    else:
        threshold = float(threshold)
        
    # Enforce constraints on modified data
    mod_copy = modified_dict.copy()
    warnings = validate_student_constraints(mod_copy)
    
    # Auto-clamp logical violations
    if "Curricular units 1st sem (enrolled)" in mod_copy and "Curricular units 1st sem (approved)" in mod_copy:
        enr = float(mod_copy["Curricular units 1st sem (enrolled)"])
        appr = float(mod_copy["Curricular units 1st sem (approved)"])
        if appr > enr:
            mod_copy["Curricular units 1st sem (approved)"] = enr
            
    if "Curricular units 2nd sem (enrolled)" in mod_copy and "Curricular units 2nd sem (approved)" in mod_copy:
        enr2 = float(mod_copy["Curricular units 2nd sem (enrolled)"])
        appr2 = float(mod_copy["Curricular units 2nd sem (approved)"])
        if appr2 > enr2 and enr2 > 0:
            mod_copy["Curricular units 2nd sem (approved)"] = enr2
            
    # Baseline and Simulated predictions
    base_pred = predict_single(baseline_dict, threshold=threshold)
    sim_pred = predict_single(mod_copy, threshold=threshold)
    
    # Delta calculations
    base_risk = base_pred["dropout_probability"]
    sim_risk = sim_pred["dropout_probability"]
    delta_risk_pp = round((sim_risk - base_risk) * 100, 2)
    
    # Track feature modifications
    changed_features = []
    for k, v in mod_copy.items():
        base_v = baseline_dict.get(k)
        if base_v is not None and float(base_v) != float(v):
            changed_features.append({
                "feature": k,
                "baseline_value": float(base_v),
                "modified_value": float(v),
                "delta": round(float(v) - float(base_v), 2)
            })
            
    # Algorithmic Recourse from baseline
    base_record = prepare_student_record(baseline_dict)
    recourse_info = counterfactual_recourse(bundle, base_record, target_threshold=threshold)
    
    return {
        "status": "success",
        "baseline": base_pred,
        "simulated": sim_pred,
        "delta_risk_pp": delta_risk_pp,
        "direction": "reduced" if delta_risk_pp < 0 else ("increased" if delta_risk_pp > 0 else "neutral"),
        "changed_features": changed_features,
        "recourse_recommendation": recourse_info,
        "warnings": warnings,
        "governance_note": (
            "Simulation displays statistical associations from historical cohort patterns only. "
            "Model predictions reflect conditional probabilities, not deterministic outcomes or guaranteed causal consequences."
        )
    }
