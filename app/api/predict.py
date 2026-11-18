"""API Endpoints for Student Predictions and Cohort Screening."""
from __future__ import annotations
import io
from flask import Blueprint, request, jsonify
from app.services.model_service import get_archetypes, get_student_by_index
from app.services.prediction_service import predict_single, predict_cohort_batch

predict_bp = Blueprint("api_predict", __name__, url_prefix="/api/predict")


@predict_bp.route("/single", methods=["POST"])
def single_prediction():
    try:
        data = request.get_json(force=True) or {}
        student_data = data.get("student", {})
        threshold = data.get("threshold")
        if threshold is not None:
            threshold = float(threshold)
            
        result = predict_single(student_data, threshold=threshold)
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@predict_bp.route("/cohort", methods=["POST"])
def cohort_screening():
    try:
        if "file" not in request.files:
            return jsonify({"status": "error", "message": "No CSV file provided in upload"}), 400
            
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"status": "error", "message": "Selected file is empty"}), 400
            
        threshold = request.form.get("threshold")
        if threshold is not None:
            threshold = float(threshold)
            
        stream = io.StringIO(file.stream.read().decode("utf-8", errors="replace"))
        result = predict_cohort_batch(stream, threshold=threshold)
        return jsonify({"status": "success", "data": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@predict_bp.route("/archetypes", methods=["GET"])
def archetypes():
    try:
        presets = get_archetypes()
        return jsonify({"status": "success", "archetypes": presets})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@predict_bp.route("/student/<int:idx>", methods=["GET"])
def student_by_index(idx: int):
    try:
        record = get_student_by_index(idx)
        return jsonify({"status": "success", "index": idx, "student": record})
    except IndexError as e:
        return jsonify({"status": "error", "message": str(e)}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
