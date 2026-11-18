"""Centralized Configuration for EduPulse Flask Application."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Config:
    SECRET_KEY = os.environ.get("EDUPULSE_SECRET_KEY", "edupulse-super-secret-key-int395-group12-2026")
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2 MB max upload
    ARTIFACTS_DIR = BASE_DIR / "artifacts"
    DATA_DIR = BASE_DIR / "data"
    DATABASE_PATH = BASE_DIR / "local_demo" / "cases.sqlite3"
    
    # Session & Security Settings
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False  # Set True if HTTPS is enabled
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours
    
    # ML & Intelligence defaults
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


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
