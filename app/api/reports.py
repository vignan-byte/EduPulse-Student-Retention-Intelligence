"""API Endpoints for Dossier Export in PDF and Markdown."""
from __future__ import annotations
import io
from flask import Blueprint, request, jsonify, send_file
from app.services.report_service import get_markdown_dossier, get_pdf_dossier

reports_bp = Blueprint("api_reports", __name__, url_prefix="/api/reports")


@reports_bp.route("/markdown", methods=["POST"])
def markdown_report():
    try:
        data = request.get_json(force=True) or {}
        student_data = data.get("student", {})
        case_ref = data.get("case_ref", "DEMO-001")
        advisor_name = data.get("advisor_name", "Academic Advisor")
        
        md_text = get_markdown_dossier(student_data, case_ref=case_ref, advisor_name=advisor_name)
        return jsonify({"status": "success", "markdown": md_text})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@reports_bp.route("/pdf", methods=["POST"])
def pdf_report():
    try:
        data = request.get_json(force=True) or {}
        student_data = data.get("student", {})
        case_ref = data.get("case_ref", "DEMO-001")
        advisor_name = data.get("advisor_name", "Academic Advisor")
        
        pdf_bytes = get_pdf_dossier(student_data, case_ref=case_ref, advisor_name=advisor_name)
        
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"Student_Dossier_{case_ref}.pdf"
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400
