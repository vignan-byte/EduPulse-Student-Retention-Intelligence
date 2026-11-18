"""Comprehensive Flask UI and Navigation Test Suite for EduPulse v11.0.

Tests that all web views render with zero exceptions, display page titles,
and load historical benchmark student #130.
"""
from pathlib import Path
import pytest
from app import create_app


@pytest.fixture(scope="module")
def client():
    app = create_app("testing")
    with app.test_client() as client:
        yield client


def test_app_loads_cleanly(client):
    """Verify application boots with zero startup exceptions and displays master title."""
    res = client.get("/")
    assert res.status_code == 200
    assert b"EduPulse" in res.data
    assert b"Student Retention Intelligence" in res.data


def test_app_historical_student_toggle(client):
    """Verify historical record #130 toggle executes real inference with zero errors."""
    res = client.get("/assessment")
    assert res.status_code == 200
    assert b"Student #130" in res.data
    assert b"Digital Twin" in res.data

    # Verify API prediction for #130
    api_res = client.get("/api/predict/student/130")
    assert api_res.status_code == 200
    pred_res = client.post("/api/predict/single", json={"student": api_res.get_json()["student"]})
    assert pred_res.status_code == 200
    prob = pred_res.get_json()["dropout_probability"]
    assert 0.0 <= prob <= 1.0


def test_all_navigation_views_render(client):
    """Iterate through major navigation views and ensure zero unhandled exceptions."""
    views_to_test = [
        "/overview",
        "/student-risk",
        "/assessment",
        "/model-performance",
        "/explainability",
        "/intervention",
        "/cohort",
        "/institutional",
        "/reliability",
        "/methodology",
        "/faculty-demo"
    ]

    for view in views_to_test:
        res = client.get(view)
        assert res.status_code == 200, f"Exception occurred while rendering view: {view}"
        assert b"EduPulse" in res.data
