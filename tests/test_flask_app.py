"""Comprehensive Flask Web Application Tests for EduPulse v11.0.

Tests all 11 application routes, template renderings, and status codes.
"""
import pytest
from app import create_app


@pytest.fixture(scope="module")
def client():
    app = create_app("testing")
    with app.test_client() as client:
        yield client


def test_overview_route(client):
    res = client.get("/overview")
    assert res.status_code == 200
    assert b"Executive Retention Dashboard" in res.data
    assert b"Target Class Distribution" in res.data


def test_root_redirects_to_overview(client):
    res = client.get("/")
    assert res.status_code == 200
    assert b"Executive Retention Dashboard" in res.data


def test_student_risk_route(client):
    res = client.get("/student-risk")
    assert res.status_code == 200
    assert b"Student Risk Intelligence" in res.data
    assert b"Batch Cohort CSV Screening" in res.data


def test_assessment_digital_twin_route(client):
    res = client.get("/assessment")
    assert res.status_code == 200
    assert b"Digital Twin Studio" in res.data
    assert b"Algorithmic Recourse Milestones" in res.data


def test_model_performance_route(client):
    res = client.get("/model-performance")
    assert res.status_code == 200
    assert b"Model Performance &amp; Benchmark Lab" in res.data or b"Model Performance & Benchmark Lab" in res.data
    assert b"Dynamic Screening Threshold Simulator" in res.data


def test_explainability_route(client):
    res = client.get("/explainability")
    assert res.status_code == 200
    assert b"Explainable AI Studio" in res.data
    assert b"SHAP Local Feature Attribution" in res.data


def test_intervention_crm_route(client):
    res = client.get("/intervention")
    assert res.status_code == 200
    assert b"Intervention Planning &amp; Advisor CRM" in res.data or b"Intervention Planning & Advisor CRM" in res.data


def test_cohort_heatmap_route(client):
    res = client.get("/cohort")
    assert res.status_code == 200
    assert b"Cohort Intelligence &amp; Risk Heatmap" in res.data or b"Cohort Intelligence & Risk Heatmap" in res.data


def test_institutional_route(client):
    res = client.get("/institutional")
    assert res.status_code == 200
    assert b"Institutional Analytics &amp; Capacity Planner" in res.data or b"Institutional Analytics & Capacity Planner" in res.data


def test_reliability_route(client):
    res = client.get("/reliability")
    assert res.status_code == 200
    assert b"Model Reliability &amp; Drift Monitor" in res.data or b"Model Reliability & Drift Monitor" in res.data


def test_methodology_route(client):
    res = client.get("/methodology")
    assert res.status_code == 200
    assert b"Methodology &amp; Retention Governance" in res.data or b"Methodology & Retention Governance" in res.data
    assert b"Zero-Leakage Decision Boundary" in res.data


def test_faculty_demo_route(client):
    res = client.get("/faculty-demo")
    assert res.status_code == 200
    assert b"9-Stage Faculty Demonstration Mode 2.0" in res.data
    assert b"Pre-Flight System Integrity &amp; Health Check" in res.data or b"Pre-Flight System Integrity & Health Check" in res.data
