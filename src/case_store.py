"""Role-checked SQLite workflow for FICTIONAL demo cases only.

This is an educational local access-control example, not production IAM.
"""
from __future__ import annotations

import hashlib
import hmac
import os
import re
import secrets
import sqlite3
from pathlib import Path

STATUSES = ("Needs assessment", "Support offered", "Follow-up planned", "Closed")
SUPPORT = ("Academic advising", "Tutoring resources", "Financial-aid information",
           "Accessibility support information", "Student wellbeing resources")


class AuthorizationError(PermissionError):
    pass


def _password_hash(password: str, salt: bytes) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 310_000).hex()


class DemoCaseStore:
    def __init__(self, path: str | Path):
        self.path = str(path)
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
              username TEXT PRIMARY KEY, salt TEXT NOT NULL, password_hash TEXT NOT NULL,
              role TEXT NOT NULL CHECK(role IN ('admin','advisor')));
            CREATE TABLE IF NOT EXISTS cases (
              reference TEXT PRIMARY KEY, owner TEXT NOT NULL REFERENCES users(username),
              status TEXT NOT NULL, support TEXT NOT NULL, updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE IF NOT EXISTS audit (
              id INTEGER PRIMARY KEY AUTOINCREMENT, actor TEXT NOT NULL, reference TEXT NOT NULL,
              action TEXT NOT NULL, happened_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
            """)

    def _connect(self):
        db = sqlite3.connect(self.path, timeout=5)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        return db

    def create_user(self, username: str, password: str, role: str,
                    actor: str | None = None, actor_password: str | None = None):
        if not re.fullmatch(r"[a-z][a-z0-9_]{2,31}", username) or role not in ("admin", "advisor"):
            raise ValueError("Invalid username or role")
        if len(password) < 12:
            raise ValueError("Password must contain at least 12 characters")
        with self._connect() as db:
            count = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            if count and (actor is None or actor_password is None or
                          self.authenticate(actor, actor_password) is None or
                          self._role(db, actor) != "admin"):
                raise AuthorizationError("Only an administrator can create another user")
            if not count and role != "admin":
                raise AuthorizationError("The first user must be an administrator")
            salt = secrets.token_bytes(16)
            db.execute("INSERT INTO users(username,salt,password_hash,role) VALUES(?,?,?,?)",
                       (username, salt.hex(), _password_hash(password, salt), role))

    def authenticate(self, username: str, password: str) -> str | None:
        with self._connect() as db:
            row = db.execute("SELECT salt,password_hash FROM users WHERE username=?", (username,)).fetchone()
        if row is None:
            # Do equivalent work for unknown users to reduce timing distinction.
            _password_hash(password, bytes(16))
            return None
        candidate = _password_hash(password, bytes.fromhex(row["salt"]))
        return username if hmac.compare_digest(candidate, row["password_hash"]) else None

    def _role(self, db, actor: str) -> str:
        row = db.execute("SELECT role FROM users WHERE username=?", (actor,)).fetchone()
        if row is None:
            raise AuthorizationError("Unknown user")
        return row["role"]

    def save_case(self, actor: str, reference: str, owner: str, status: str, supports: list[str]):
        if not re.fullmatch(r"DEMO-[A-Za-z0-9-]{1,24}", reference):
            raise ValueError("Only DEMO- fictional references are supported")
        if status not in STATUSES or any(s not in SUPPORT for s in supports):
            raise ValueError("Invalid case status or support option")
        with self._connect() as db:
            role = self._role(db, actor)
            owner_role = self._role(db, owner)
            if owner_role != "advisor":
                raise ValueError("Case owner must be an advisor")
            if actor != owner and role != "admin":
                raise AuthorizationError("Cannot manage another advisor's case")
            existing = db.execute("SELECT owner FROM cases WHERE reference=?", (reference,)).fetchone()
            if existing and existing["owner"] != owner and role != "admin":
                raise AuthorizationError("Cannot transfer another advisor's case")
            db.execute("""INSERT INTO cases(reference,owner,status,support) VALUES(?,?,?,?)
                ON CONFLICT(reference) DO UPDATE SET owner=excluded.owner,
                status=excluded.status, support=excluded.support, updated_at=CURRENT_TIMESTAMP""",
                       (reference, owner, status, ", ".join(sorted(set(supports)))))
            db.execute("INSERT INTO audit(actor,reference,action) VALUES(?,?,?)",
                       (actor, reference, "create" if existing is None else "update"))

    def list_cases(self, actor: str):
        with self._connect() as db:
            role = self._role(db, actor)
            query = "SELECT reference,owner,status,support,updated_at FROM cases"
            rows = (db.execute(query + " ORDER BY reference") if role == "admin" else
                    db.execute(query + " WHERE owner=? ORDER BY reference", (actor,)))
            return [dict(row) for row in rows]

    def list_advisors(self, actor: str):
        with self._connect() as db:
            if self._role(db, actor) != "admin":
                raise AuthorizationError("Only administrators can list advisor accounts")
            return [row["username"] for row in db.execute(
                "SELECT username FROM users WHERE role='advisor' ORDER BY username")]

    def role_for(self, actor: str):
        with self._connect() as db:
            return self._role(db, actor)

    def audit_history(self, actor: str):
        with self._connect() as db:
            if self._role(db, actor) != "admin":
                raise AuthorizationError("Only administrators can inspect the audit history")
            return [dict(row) for row in db.execute("SELECT * FROM audit ORDER BY id")]

    def delete_case(self, actor: str, reference: str):
        """Delete a fictional case; retain minimal action metadata in audit."""
        with self._connect() as db:
            role = self._role(db, actor)
            row = db.execute("SELECT owner FROM cases WHERE reference=?", (reference,)).fetchone()
            if row is None:
                return False
            if role != "admin" and row["owner"] != actor:
                raise AuthorizationError("Cannot delete another advisor's case")
            db.execute("DELETE FROM cases WHERE reference=?", (reference,))
            db.execute("INSERT INTO audit(actor,reference,action) VALUES(?,?,?)",
                       (actor, reference, "delete"))
            return True

    def record_followup(self, actor, reference, due_date, outcome):
        """Structured follow-up only: no free text student disclosures."""
        from datetime import date
        date.fromisoformat(due_date)
        if outcome not in ('Pending', 'Contacted', 'Support accepted', 'Support declined', 'No response'):
            raise ValueError('Invalid follow-up outcome')
        with self._connect() as db:
            role = self._role(db, actor)
            case = db.execute('SELECT owner FROM cases WHERE reference=?', (reference,)).fetchone()
            if case is None or (role != 'admin' and case['owner'] != actor):
                raise AuthorizationError('Case unavailable')
            db.execute('CREATE TABLE IF NOT EXISTS followups (id INTEGER PRIMARY KEY, reference TEXT REFERENCES cases(reference) ON DELETE CASCADE, due_date TEXT, outcome TEXT)')
            db.execute('INSERT INTO followups(reference,due_date,outcome) VALUES(?,?,?)', (reference, due_date, outcome))
            db.execute('INSERT INTO audit(actor,reference,action) VALUES(?,?,?)', (actor, reference, 'followup:' + outcome))

    def list_followups(self, actor):
        with self._connect() as db:
            role = self._role(db, actor)
            if not db.execute("SELECT name FROM sqlite_master WHERE name='followups'").fetchone():
                return []
            query = 'SELECT f.* FROM followups f JOIN cases c ON c.reference=f.reference'
            rows = db.execute(query if role == 'admin' else query + ' WHERE c.owner=?', () if role == 'admin' else (actor,))
            return [dict(r) for r in rows]
