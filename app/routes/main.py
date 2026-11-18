"""Main Navigation and Page Rendering Blueprints for EduPulse."""
from __future__ import annotations
import json
from pathlib import Path
from flask import Blueprint, render_template, current_app
from app.services.model_service import (
    get_overview_statistics, get_metrics, get_archetypes, get_student_by_index,
    get_raw_data, get_bundle
)
from app.services.case_service import get_case_statuses, get_support_options

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
@main_bp.route("/overview")
def overview():
    stats = get_overview_statistics()
    metrics = get_metrics()
    return render_template("overview.html", active_page="overview", stats=stats, metrics=metrics)


@main_bp.route("/student-risk")
def student_risk():
    archetypes = get_archetypes()
    metrics = get_metrics()
    threshold = float(metrics.get("selected_screening_threshold", 0.38))
    return render_template("student_risk.html", active_page="student_risk", archetypes=archetypes, threshold=threshold)


@main_bp.route("/assessment")
def assessment():
    archetypes = get_archetypes()
    metrics = get_metrics()
    threshold = float(metrics.get("selected_screening_threshold", 0.38))
    student_130 = get_student_by_index(130)
    return render_template("assessment.html", active_page="assessment", archetypes=archetypes, student_130=student_130, threshold=threshold)


@main_bp.route("/model-performance")
def model_performance():
    metrics = get_metrics()
    scenarios = metrics.get("threshold_scenarios", [])
    model_comparison = metrics.get("model_comparison", {})
    return render_template("model_performance.html", active_page="model_performance", metrics=metrics, scenarios=scenarios, model_comparison=model_comparison)


@main_bp.route("/explainability")
def explainability():
    archetypes = get_archetypes()
    student_130 = get_student_by_index(130)
    return render_template("explainability.html", active_page="explainability", archetypes=archetypes, student_130=student_130)


@main_bp.route("/intervention")
def intervention():
    statuses = get_case_statuses()
    supports = get_support_options()
    return render_template("intervention.html", active_page="intervention", statuses=statuses, supports=supports)


@main_bp.route("/cohort")
def cohort():
    raw_df = get_raw_data()
    return render_template("cohort.html", active_page="cohort", total_students=len(raw_df))


@main_bp.route("/institutional")
def institutional():
    metrics = get_metrics()
    return render_template("institutional.html", active_page="institutional", metrics=metrics)


@main_bp.route("/reliability")
def reliability():
    artifacts_dir = current_app.config.get("ARTIFACTS_DIR", Path("artifacts"))
    manifest_path = artifacts_dir / "manifest.json"
    manifest_data = {}
    if manifest_path.exists():
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest_data = json.load(f)
        except Exception:
            pass
    metrics = get_metrics()
    return render_template("reliability.html", active_page="reliability", manifest=manifest_data, metrics=metrics)


@main_bp.route("/methodology")
def methodology():
    metrics = get_metrics()
    bundle = get_bundle()
    return render_template("methodology.html", active_page="methodology", metrics=metrics, features=bundle["features"])


@main_bp.route("/faculty-demo")
def faculty_demo():
    metrics = get_metrics()
    threshold = float(metrics.get("selected_screening_threshold", 0.38))
    student_130 = get_student_by_index(130)
    archetypes = get_archetypes()
    return render_template("faculty_demo.html", active_page="faculty_demo", threshold=threshold, student_130=student_130, archetypes=archetypes, metrics=metrics)
