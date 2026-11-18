"""Case Service: wraps DemoCaseStore for student retention cases, follow-ups, and audit trail."""
from __future__ import annotations
from app.services.model_service import get_case_store
from src.case_store import AuthorizationError, STATUSES, SUPPORT


def authenticate_user(username: str, password: str) -> str | None:
    store = get_case_store()
    return store.authenticate(username, password)


def get_user_role(actor: str) -> str:
    store = get_case_store()
    return store.role_for(actor)


def get_cases(actor: str) -> list[dict]:
    store = get_case_store()
    return store.list_cases(actor)


def save_case(actor: str, reference: str, owner: str, status: str, supports: list[str]) -> bool:
    store = get_case_store()
    store.save_case(actor, reference, owner, status, supports)
    return True


def delete_case(actor: str, reference: str) -> bool:
    store = get_case_store()
    return store.delete_case(actor, reference)


def list_advisors(actor: str) -> list[str]:
    store = get_case_store()
    return store.list_advisors(actor)


def record_followup(actor: str, reference: str, due_date: str, outcome: str) -> bool:
    store = get_case_store()
    store.record_followup(actor, reference, due_date, outcome)
    return True


def list_followups(actor: str) -> list[dict]:
    store = get_case_store()
    return store.list_followups(actor)


def get_audit_trail(actor: str) -> list[dict]:
    store = get_case_store()
    return store.audit_history(actor)


def get_case_statuses() -> list[str]:
    return list(STATUSES)


def get_support_options() -> list[str]:
    return list(SUPPORT)
