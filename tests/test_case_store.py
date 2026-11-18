import pytest

from src.case_store import AuthorizationError, DemoCaseStore


@pytest.fixture
def store(tmp_path):
    db = DemoCaseStore(tmp_path / "demo.sqlite3")
    db.create_user("admin", "admin-secret-password", "admin")
    db.create_user("advisor1", "advisor-one-password", "advisor", "admin", "admin-secret-password")
    db.create_user("advisor2", "advisor-two-password", "advisor", "admin", "admin-secret-password")
    return db


def test_authentication_passwords_hashed(store):
    assert store.authenticate("advisor1", "advisor-one-password") == "advisor1"
    assert store.authenticate("advisor1", "incorrect") is None
    assert store.authenticate("unknown", "anything") is None


def test_cross_advisor_case_access_denied(store):
    store.save_case("advisor1", "DEMO-001", "advisor1", "Needs assessment", ["Academic advising"])
    assert len(store.list_cases("advisor1")) == 1
    assert store.list_cases("advisor2") == []
    with pytest.raises(AuthorizationError):
        store.save_case("advisor2", "DEMO-001", "advisor1", "Closed", [])
    assert store.list_cases("advisor1")[0]["status"] == "Needs assessment"


def test_admin_can_view_and_reassign(store):
    store.save_case("advisor1", "DEMO-002", "advisor1", "Needs assessment", [])
    store.save_case("admin", "DEMO-002", "advisor2", "Follow-up planned", ["Tutoring resources"])
    assert store.list_cases("advisor1") == []
    assert len(store.list_cases("advisor2")) == 1
    assert len(store.audit_history("admin")) == 2
    with pytest.raises(AuthorizationError):
        store.audit_history("advisor2")


def test_invalid_content_and_user_creation_blocked(store):
    with pytest.raises(ValueError):
        store.save_case("advisor1", "REAL-123", "advisor1", "Closed", [])
    with pytest.raises(ValueError):
        store.save_case("advisor1", "DEMO-123", "advisor1", "Closed", ["Unknown medical advice"])
    with pytest.raises(AuthorizationError):
        store.create_user("thirduser", "long-enough-password", "advisor", "admin", "wrong")
    with pytest.raises(ValueError):
        store.create_user("fourth", "short", "advisor", "admin", "admin-secret-password")


def test_delete_requires_ownership_and_keeps_audit(store):
    store.save_case("advisor1", "DEMO-DELETE", "advisor1", "Needs assessment", [])
    with pytest.raises(AuthorizationError):
        store.delete_case("advisor2", "DEMO-DELETE")
    assert store.delete_case("advisor1", "DEMO-DELETE") is True
    assert store.list_cases("advisor1") == []
    assert store.audit_history("admin")[-1]["action"] == "delete"
