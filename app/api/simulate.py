"""API Endpoint for Digital Twin What-If Counterfactual Simulation."""
from __future__ import annotations
from flask import Blueprint, request, jsonify
from app.services.simulation_service import simulate_digital_twin

simulate_bp = Blueprint("api_simulate", __name__, url_prefix="/api/simulate")


@simulate_bp.route("", methods=["POST"])
def simulate():
    try:
        data = request.get_json(force=True) or {}
        baseline = data.get("baseline", {})
        modified = data.get("modified", {})
        threshold = data.get("threshold")
        if threshold is not None:
            threshold = float(threshold)
            
        result = simulate_digital_twin(baseline, modified, threshold=threshold)
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400
