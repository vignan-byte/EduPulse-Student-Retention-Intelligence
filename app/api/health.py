"""API Endpoints for Health Checks, System Diagnostics, and Drift Reporting."""
from __future__ import annotations
from flask import Blueprint, jsonify, request
from app.services.monitoring_service import get_model_health_check, get_drift_analysis

health_bp = Blueprint("api_health", __name__, url_prefix="/api/health")


@health_bp.route("", methods=["GET"])
def health():
    try:
        force_refresh = request.args.get("refresh", "").lower() in ("true", "1", "yes")
        report = get_model_health_check(force_refresh=force_refresh)
        return jsonify(report)
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)}), 500


@health_bp.route("/live", methods=["GET"])
@health_bp.route("/ping", methods=["GET"])
def live():
    """Ultra-fast, non-blocking liveness probe for cloud platform healthcheck pings."""
    return jsonify({"status": "UP"}), 200


@health_bp.route("/drift", methods=["GET"])
def drift():
    try:
        report = get_drift_analysis()
        return jsonify({"status": "success", "drift_report": report})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
