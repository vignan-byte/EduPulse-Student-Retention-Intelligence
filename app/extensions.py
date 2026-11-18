"""Application Singletons and Extension Registries for EduPulse."""
from pathlib import Path
import pandas as pd

from src.case_store import DemoCaseStore
from src.registry import verified_load
from src.ml import load_data


class ModelManager:
    """Thread-safe singleton managing the loaded ML bundle and evaluation metrics."""
    def __init__(self):
        self.bundle = None
        self.metrics = None
        self.df_raw = None
        self.case_store = None
        self.is_loaded = False

    def init_app(self, app):
        artifacts_dir = app.config.get("ARTIFACTS_DIR", Path("artifacts"))
        data_path = app.config.get("REFERENCE_DATASET", Path("data/students.csv"))
        db_path = app.config.get("DATABASE_PATH", Path("local_demo/cases.sqlite3"))
        
        # 1. Verified Model Load
        self.bundle, self.metrics = verified_load(artifacts_dir)
        
        # 2. Reference Dataset Load
        self.df_raw = load_data(str(data_path))
        
        # 3. SQLite Case Store
        self.case_store = DemoCaseStore(str(db_path))
        with self.case_store._connect() as db:
            user_count = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            if user_count == 0:
                self.case_store.create_user("admin", "Admin12345678!", "admin")
                self.case_store.create_user("advisor1", "Advisor12345678!", "advisor", actor="admin", actor_password="Admin12345678!")
        
        self.is_loaded = True
        app.logger.info("EduPulse ModelManager initialized successfully: Model=%s, Stage=%s, Rows=%d",
                        self.metrics.get("selected_model"), self.bundle.get("stage"), len(self.df_raw))


model_manager = ModelManager()
