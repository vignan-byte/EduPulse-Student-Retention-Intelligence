"""EduPulse API Blueprints Registration."""
from __future__ import annotations
from flask import Flask
from app.api.predict import predict_bp
from app.api.simulate import simulate_bp
from app.api.explain import explain_bp
from app.api.analytics import analytics_bp
from app.api.cases import cases_bp
from app.api.reports import reports_bp
from app.api.health import health_bp


def register_api_blueprints(app: Flask):
    app.register_blueprint(predict_bp)
    app.register_blueprint(simulate_bp)
    app.register_blueprint(explain_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(cases_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(health_bp)
