"""Focused deployment security regressions."""
import pytest
from app import create_app


@pytest.fixture
def client():
    app = create_app("testing")
    with app.test_client() as test_client:
        yield test_client


def test_anonymous_mutations_require_csrf(client):
    for method, path in [
        ("POST", "/api/cases/login"),
        ("POST", "/api/cases/logout"),
        ("POST", "/api/cases"),
        ("DELETE", "/api/cases/DEMO-130"),
    ]:
        response = client.open(path, method=method, json={})
        assert response.status_code == 403


def test_csrf_token_issued_to_anonymous_session(client):
    response = client.get("/api/cases/session")
    assert response.status_code == 200
    data = response.get_json()
    assert data["logged_in"] is False
    assert len(data["csrf_token"]) >= 32


def test_invalid_csrf_rejected(client):
    client.get("/api/cases/session")
    response = client.post(
        "/api/cases/login",
        json={"username": "nonexistent", "password": "incorrect"},
        headers={"X-CSRF-Token": "invalid"},
    )
    assert response.status_code == 403


def test_production_rejects_missing_secrets(monkeypatch):
    monkeypatch.delenv("EDUPULSE_SECRET_KEY", raising=False)
    monkeypatch.delenv("EDUPULSE_ADMIN_PASSWORD", raising=False)
    from config import ProductionConfig
    with pytest.raises(RuntimeError):
        ProductionConfig.validate()
