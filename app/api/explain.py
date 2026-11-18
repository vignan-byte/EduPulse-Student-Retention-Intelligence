"""API Endpoints for SHAP and LIME Explainability."""
from __future__ import annotations
from flask import Blueprint, request, jsonify
from app.services.explanation_service import compute_shap, compute_lime

explain_bp = Blueprint("api_explain", __name__, url_prefix="/api/explain")


@explain_bp.route("/shap", methods=["POST"])
def shap_explanation():
    try:
        data = request.get_json(force=True) or {}
        student_data = data.get("student", {})
        top_n = int(data.get("top_n", 12))
        max_bg = int(data.get("max_background", 25))
        
        result = compute_shap(student_data, max_background=max_bg, top_n=top_n)
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@explain_bp.route("/lime", methods=["POST"])
def lime_explanation():
    try:
        data = request.get_json(force=True) or {}
        student_data = data.get("student", {})
        top_n = int(data.get("top_n", 10))
        
        result = compute_lime(student_data, top_n=top_n)
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400
