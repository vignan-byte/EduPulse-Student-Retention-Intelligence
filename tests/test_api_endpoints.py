"""Comprehensive REST API Endpoint Tests for EduPulse v11.0."""
import json
import io
import pytest
from app import create_app


@pytest.fixture(scope="module")
def client():
    app = create_app("testing")
    store = app.extensions["model_manager"].case_store
    with store._connect() as db:
        users = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if not users:
        store.create_user("admin", "Admin12345678!", "admin")
        store.create_user("advisor1", "Advisor12345678!", "advisor",
                          actor="admin", actor_password="Admin12345678!")
    with app.test_client() as client:
        yield client


def test_api_predict_archetypes(client):
    res = client.get("/api/predict/archetypes")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert "High Risk (Academic Difficulty & Tuition Arrears)" in data["archetypes"]


def test_api_predict_student_index(client):
    res = client.get("/api/predict/student/130")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["index"] == 130
    assert "Curricular units 1st sem (approved)" in data["student"]


def test_api_predict_single(client):
    student_payload = {
        "Curricular units 1st sem (enrolled)": 6.0,
        "Curricular units 1st sem (approved)": 1.0,
        "Curricular units 1st sem (grade)": 10.2,
        "Admission grade": 115.0,
        "Debtor": 1,
        "Tuition fees up to date": 0,
        "Scholarship holder": 0
    }
    res = client.post("/api/predict/single", json={"student": student_payload, "threshold": 0.38})
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert "Dropout" in data["probabilities"]
    assert data["dropout_probability"] >= 0.50
    assert data["is_screened"] is True
    assert data["review_priority"] == "Advisor review"
    assert len(data["recommendations"]) > 0


def test_api_simulate_digital_twin(client):
    baseline = {
        "Curricular units 1st sem (enrolled)": 6.0,
        "Curricular units 1st sem (approved)": 1.0,
        "Curricular units 1st sem (grade)": 10.2,
        "Admission grade": 115.0,
        "Debtor": 1,
        "Tuition fees up to date": 0,
        "Scholarship holder": 0
    }
    modified = {
        **baseline,
        "Curricular units 1st sem (approved)": 4.0,
        "Curricular units 1st sem (grade)": 13.5,
        "Debtor": 0,
        "Tuition fees up to date": 1
    }
    res = client.post("/api/simulate", json={"baseline": baseline, "modified": modified, "threshold": 0.38})
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["delta_risk_pp"] < 0  # Risk must be reduced
    assert data["direction"] == "reduced"
    assert "recourse_recommendation" in data


def test_api_analytics_threshold(client):
    res = client.post("/api/analytics/threshold", json={"threshold": 0.38})
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["threshold"] == 0.38
    assert "metrics" in data
    assert data["metrics"]["recall"] > 0.70
    assert "confusion_matrix" in data
    assert data["confusion_matrix"]["tp"] > 200


def test_api_analytics_heatmap(client):
    res = client.get("/api/analytics/heatmap?dimension=academics")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert len(data["x_categories"]) > 0
    assert len(data["y_categories"]) > 0
    assert len(data["z_values"]) > 0


def test_api_analytics_capacity(client):
    res = client.post("/api/analytics/capacity", json={
        "total_students": 1200,
        "advisor_count": 4,
        "max_caseload": 60,
        "avg_tuition": 5000.0
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    plan = data["plan"]
    assert plan["total_advisor_capacity"] == 240
    assert len(plan["scenarios"]) > 0


def test_api_health(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] in ("HEALTHY", "DEGRADED")
    assert len(data["checks"]) >= 4


def test_api_health_drift(client):
    res = client.get("/api/health/drift")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert "drift_report" in data


def test_api_reports_markdown(client):
    student = {
        "Curricular units 1st sem (enrolled)": 6.0,
        "Curricular units 1st sem (approved)": 1.0,
        "Curricular units 1st sem (grade)": 10.2,
        "Admission grade": 115.0,
        "Debtor": 1,
        "Tuition fees up to date": 0,
        "Scholarship holder": 0
    }
    res = client.post("/api/reports/markdown", json={
        "student": student,
        "case_ref": "DEMO-TEST",
        "advisor_name": "Test Advisor"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert "# Academic Retention & Support Dossier" in data["markdown"]


def test_api_reports_pdf(client):
    student = {
        "Curricular units 1st sem (enrolled)": 6.0,
        "Curricular units 1st sem (approved)": 1.0,
        "Curricular units 1st sem (grade)": 10.2,
        "Admission grade": 115.0,
        "Debtor": 1,
        "Tuition fees up to date": 0,
        "Scholarship holder": 0
    }
    res = client.post("/api/reports/pdf", json={
        "student": student,
        "case_ref": "DEMO-TEST",
        "advisor_name": "Test Advisor"
    })
    assert res.status_code == 200
    assert res.mimetype == "application/pdf"
    assert len(res.data) > 500


def test_api_cases_authentication_and_crud(client):
    # 1. Login with bad credentials
    csrf = client.get("/api/cases/session").get_json()["csrf_token"]
    headers = {"X-CSRF-Token": csrf}
    bad_res = client.post("/api/cases/login", json={"username": "admin", "password": "WrongPassword!"}, headers=headers)
    assert bad_res.status_code == 401

    # 2. Login as admin
    login_res = client.post("/api/cases/login", json={"username": "admin", "password": "Admin12345678!"}, headers=headers)
    assert login_res.status_code == 200
    assert login_res.get_json()["status"] == "success"

    # Login rotates the CSRF token.
    headers = {"X-CSRF-Token": client.get("/api/cases/session").get_json()["csrf_token"]}
    # 3. Create a test case
    create_res = client.post("/api/cases", json={
        "reference": "DEMO-UNITTEST-01",
        "owner": "advisor1",
        "status": "Needs assessment",
        "supports": ["Academic advising", "Tutoring resources"]
    }, headers=headers)
    assert create_res.status_code == 200

    # 4. List cases
    list_res = client.get("/api/cases")
    assert list_res.status_code == 200
    cases = list_res.get_json()["cases"]
    assert any(c["reference"] == "DEMO-UNITTEST-01" for c in cases)

    # 5. Delete test case
    del_res = client.delete("/api/cases/DEMO-UNITTEST-01", headers=headers)
    assert del_res.status_code == 200

    # 6. Logout
    logout_res = client.post("/api/cases/logout", headers=headers)
    assert logout_res.status_code == 200
