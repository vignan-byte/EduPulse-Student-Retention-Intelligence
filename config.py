"""Centralized configuration for EduPulse Flask."""
import os
from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Config:
    SECRET_KEY = os.environ.get("EDUPULSE_SECRET_KEY", "edupulse-super-secret-key-int395-group12-2026")
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024
    ARTIFACTS_DIR = BASE_DIR / "artifacts"
    DATA_DIR = BASE_DIR / "data"
    DATABASE_PATH = Path(os.environ.get("EDUPULSE_DATABASE_PATH", str(BASE_DIR / "local_demo" / "cases.sqlite3")))
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SCREENING_THRESHOLD = 0.38
    REFERENCE_DATASET = DATA_DIR / "students.csv"
    CANDIDATE_DATASET = DATA_DIR / "independent_cohort.csv"

class DevelopmentConfig(Config):
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    TESTING = True
    DEBUG = False
    DATABASE_PATH = BASE_DIR / "local_demo" / "test_cases.sqlite3"

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    # Render's default filesystem is ephemeral. Use a persistent disk or an external DB
    # if CRM writes must survive restarts. Never use the tracked demonstration database.
    DATABASE_PATH = Path(os.environ.get("EDUPULSE_DATABASE_PATH", "/tmp/edupulse/cases.sqlite3"))
    SECRET_KEY = os.environ.get("EDUPULSE_SECRET_KEY")
    @classmethod
    def validate(cls):
        if not cls.SECRET_KEY or len(cls.SECRET_KEY) < 32:
            raise RuntimeError("Production requires EDUPULSE_SECRET_KEY of at least 32 characters")
        if not os.environ.get("EDUPULSE_ADMIN_PASSWORD"):
            raise RuntimeError("Production requires EDUPULSE_ADMIN_PASSWORD for fresh CRM bootstrap")
        if len(os.environ["EDUPULSE_ADMIN_PASSWORD"]) < 12:
            raise RuntimeError("EDUPULSE_ADMIN_PASSWORD must be at least 12 characters")

config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
