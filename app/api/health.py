"""API Endpoints for Health Checks, System Diagnostics, and Drift Reporting."""
from __future__ import annotations
from flask import Blueprint, jsonify
from app.services.monitoring_service import get_model_health_check, get_drift_analysis

health_bp = Blueprint("api_health", __name__, url_prefix="/api/health")


@health_bp.route("", methods=["GET"])
def health():
    try:
        report = get_model_health_check()
        return jsonify(report)
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)}), 500


@health_bp.route("/drift", methods=["GET"])
def drift():
    try:
        report = get_drift_analysis()
        return jsonify({"status": "success", "drift_report": report})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
