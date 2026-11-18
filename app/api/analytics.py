"""API Endpoints for Analytics: Dynamic Threshold, Cohort Heatmap, and Institutional Capacity Planner."""
from __future__ import annotations
import numpy as np
import pandas as pd
from flask import Blueprint, request, jsonify
from app.services.model_service import get_bundle, get_metrics, get_raw_data
from src.intelligence import compute_cohort_heatmap, advisor_capacity_planner
from src.ml import train_test_split

analytics_bp = Blueprint("api_analytics", __name__, url_prefix="/api/analytics")

# Cache test set probabilities for sub-millisecond dynamic threshold simulation
_TEST_PROBS = None
_TEST_TARGETS = None


def _get_test_predictions():
    global _TEST_PROBS, _TEST_TARGETS
    if _TEST_PROBS is None or _TEST_TARGETS is None:
        bundle = get_bundle()
        raw_df = get_raw_data()
        _, test_df = train_test_split(raw_df, test_size=0.2, random_state=42, stratify=raw_df["Target"])
        
        classes = list(bundle["model"].classes_)
        dropout_idx = classes.index("Dropout")
        
        probs = bundle["model"].predict_proba(test_df[bundle["features"]])[:, dropout_idx]
        is_dropout = (test_df["Target"].astype(str).str.strip() == "Dropout").to_numpy(dtype=int)
        
        _TEST_PROBS = probs
        _TEST_TARGETS = is_dropout
        
    return _TEST_PROBS, _TEST_TARGETS


@analytics_bp.route("/threshold", methods=["POST"])
def evaluate_threshold():
    try:
        data = request.get_json(force=True) or {}
        threshold = float(data.get("threshold", 0.38))
        threshold = max(0.01, min(0.99, threshold))
        
        probs, targets = _get_test_predictions()
        
        predicted_positives = (probs >= threshold).astype(int)
        
        tp = int(np.sum((predicted_positives == 1) & (targets == 1)))
        fp = int(np.sum((predicted_positives == 1) & (targets == 0)))
        fn = int(np.sum((predicted_positives == 0) & (targets == 1)))
        tn = int(np.sum((predicted_positives == 0) & (targets == 0)))
        
        total_positives = tp + fn
        total_negatives = tn + fp
        total_samples = len(targets)
        flagged_count = tp + fp
        
        precision = round(tp / flagged_count, 4) if flagged_count > 0 else 0.0
        recall = round(tp / total_positives, 4) if total_positives > 0 else 0.0
        specificity = round(tn / total_negatives, 4) if total_negatives > 0 else 0.0
        f1 = round(2 * (precision * recall) / (precision + recall), 4) if (precision + recall) > 0 else 0.0
        accuracy = round((tp + tn) / total_samples, 4)
        
        return jsonify({
            "status": "success",
            "threshold": round(threshold, 2),
            "test_samples": total_samples,
            "metrics": {
                "precision": precision,
                "recall": recall,
                "sensitivity": recall,
                "specificity": specificity,
                "f1_score": f1,
                "accuracy": accuracy,
                "flagged_count": flagged_count,
                "flagged_percentage": round((flagged_count / total_samples) * 100, 1)
            },
            "confusion_matrix": {
                "tp": tp,
                "fp": fp,
                "fn": fn,
                "tn": tn,
                "display": [
                    [tp, fn],
                    [fp, tn]
                ],
                "labels": ["Flagged (Positive)", "Unflagged (Negative)"],
                "actual_labels": ["Actual Dropout", "Actual Non-Dropout"]
            }
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@analytics_bp.route("/heatmap", methods=["GET"])
def cohort_heatmap():
    try:
        dimension = request.args.get("dimension", "academics")
        raw_df = get_raw_data()
        
        data = compute_cohort_heatmap(raw_df, dimension=dimension)
        rate_matrix = data["rate_matrix"]
        count_matrix = data["count_matrix"]
        
        # Structure for Plotly.js Heatmap
        x_categories = list(rate_matrix.columns)
        y_categories = list(rate_matrix.index)
        z_values = rate_matrix.values.round(4).tolist()
        text_matrix = []
        
        for i in range(len(y_categories)):
            row_text = []
            for j in range(len(x_categories)):
                rate = float(rate_matrix.iloc[i, j])
                cnt = int(count_matrix.iloc[i, j])
                warning = " ⚠️ N<30" if (cnt > 0 and cnt < 30) else ""
                row_text.append(f"{rate:.1%}<br>(N={cnt}){warning}")
            text_matrix.append(row_text)
            
        return jsonify({
            "status": "success",
            "dimension": dimension,
            "x_label": data["x_label"],
            "y_label": data["y_label"],
            "x_categories": x_categories,
            "y_categories": y_categories,
            "z_values": z_values,
            "text_matrix": text_matrix,
            "total_students": data["total_students"]
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@analytics_bp.route("/capacity", methods=["POST"])
def capacity_planner():
    try:
        data = request.get_json(force=True) or {}
        metrics = get_metrics()
        
        total_students = int(data.get("total_students", 1200))
        advisor_count = int(data.get("advisor_count", 4))
        max_caseload = int(data.get("max_caseload", 60))
        avg_tuition = float(data.get("avg_tuition", 5000.0))
        
        plan = advisor_capacity_planner(
            metrics=metrics,
            total_students=total_students,
            advisor_count=advisor_count,
            max_caseload=max_caseload,
            avg_tuition=avg_tuition
        )
        return jsonify({"status": "success", "plan": plan})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400
