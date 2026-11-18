"""API Endpoints for Case Management, Follow-ups, and Advisor CRM."""
from __future__ import annotations
from flask import Blueprint, request, jsonify, session
from app.services.case_service import (
    authenticate_user, get_user_role, get_cases, save_case, delete_case,
    list_advisors, record_followup, list_followups, get_audit_trail,
    get_case_statuses, get_support_options
)
from src.case_store import AuthorizationError

cases_bp = Blueprint("api_cases", __name__, url_prefix="/api/cases")


def _get_current_user():
    username = session.get("username")
    if not username:
        return None, None
    role = session.get("role", "advisor")
    return username, role


@cases_bp.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json(force=True) or {}
        username = (data.get("username") or "").strip().lower()
        password = data.get("password") or ""
        
        authenticated_user = authenticate_user(username, password)
        if not authenticated_user:
            return jsonify({"status": "error", "message": "Invalid username or password"}), 401
            
        role = get_user_role(authenticated_user)
        session["username"] = authenticated_user
        session["role"] = role
        
        return jsonify({
            "status": "success",
            "username": authenticated_user,
            "role": role,
            "message": f"Welcome back, {authenticated_user} ({role.upper()})"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@cases_bp.route("/logout", methods=["POST"])
def logout():
    session.pop("username", None)
    session.pop("role", None)
    return jsonify({"status": "success", "message": "Logged out successfully"})


@cases_bp.route("/session", methods=["GET"])
def session_status():
    user, role = _get_current_user()
    if not user:
        return jsonify({"logged_in": False})
    return jsonify({
        "logged_in": True,
        "username": user,
        "role": role,
        "statuses": get_case_statuses(),
        "supports": get_support_options()
    })


@cases_bp.route("", methods=["GET"])
def list_all_cases():
    user, _ = _get_current_user()
    if not user:
        return jsonify({"status": "error", "message": "Authentication required"}), 401
    try:
        cases = get_cases(user)
        return jsonify({"status": "success", "cases": cases})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@cases_bp.route("", methods=["POST"])
def create_or_update_case():
    user, role = _get_current_user()
    if not user:
        return jsonify({"status": "error", "message": "Authentication required"}), 401
    try:
        data = request.get_json(force=True) or {}
        reference = (data.get("reference") or "").strip()
        owner = (data.get("owner") or user).strip().lower()
        status = data.get("status", "Needs assessment")
        supports = data.get("supports", [])
        
        if not reference.startswith("DEMO-"):
            reference = f"DEMO-{reference}"
            
        save_case(user, reference, owner, status, supports)
        return jsonify({"status": "success", "message": f"Case {reference} saved successfully"})
    except AuthorizationError as e:
        return jsonify({"status": "error", "message": str(e)}), 403
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@cases_bp.route("/<reference>", methods=["DELETE"])
def remove_case(reference: str):
    user, _ = _get_current_user()
    if not user:
        return jsonify({"status": "error", "message": "Authentication required"}), 401
    try:
        deleted = delete_case(user, reference)
        if not deleted:
            return jsonify({"status": "error", "message": "Case not found"}), 404
        return jsonify({"status": "success", "message": f"Case {reference} deleted successfully"})
    except AuthorizationError as e:
        return jsonify({"status": "error", "message": str(e)}), 403
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@cases_bp.route("/advisors", methods=["GET"])
def advisors():
    user, role = _get_current_user()
    if not user or role != "admin":
        return jsonify({"status": "error", "message": "Admin privileges required"}), 403
    try:
        adv_list = list_advisors(user)
        return jsonify({"status": "success", "advisors": adv_list})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@cases_bp.route("/followup", methods=["POST"])
def record_case_followup():
    user, _ = _get_current_user()
    if not user:
        return jsonify({"status": "error", "message": "Authentication required"}), 401
    try:
        data = request.get_json(force=True) or {}
        reference = data.get("reference")
        due_date = data.get("due_date")
        outcome = data.get("outcome")
        
        record_followup(user, reference, due_date, outcome)
        return jsonify({"status": "success", "message": "Follow-up saved successfully"})
    except AuthorizationError as e:
        return jsonify({"status": "error", "message": str(e)}), 403
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@cases_bp.route("/followups", methods=["GET"])
def followups_list():
    user, _ = _get_current_user()
    if not user:
        return jsonify({"status": "error", "message": "Authentication required"}), 401
    try:
        f_list = list_followups(user)
        return jsonify({"status": "success", "followups": f_list})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@cases_bp.route("/audit", methods=["GET"])
def audit_history():
    user, role = _get_current_user()
    if not user or role != "admin":
        return jsonify({"status": "error", "message": "Admin privileges required"}), 403
    try:
        history = get_audit_trail(user)
        return jsonify({"status": "success", "audit": history})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400
