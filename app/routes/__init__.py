"""EduPulse Web Routes Registration."""
from __future__ import annotations
from flask import Flask
from app.routes.main import main_bp


def register_routes(app: Flask):
    app.register_blueprint(main_bp)
