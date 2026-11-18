"""EduPulse Flask Application Factory."""
from __future__ import annotations
import os
from flask import Flask, jsonify, render_template, request
from config import config_by_name
from app.extensions import model_manager
from app.routes import register_routes
from app.api import register_api_blueprints


def create_app(config_name: str | None = None) -> Flask:
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "default")
        
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static"
    )
    
    # 1. Load Configuration
    cfg = config_by_name.get(config_name, config_by_name["default"])
    if config_name == "production":
        cfg.validate()
    app.config.from_object(cfg)
    
    # 2. Initialize Singletons & ML Engine
    model_manager.init_app(app)
    app.extensions["model_manager"] = model_manager
    
    # 3. Register Blueprints
    register_routes(app)
    register_api_blueprints(app)
    
    # 4. Context Processors for Templates
    @app.context_processor
    def inject_metadata():
        return {
            "app_version": "11.0.0",
            "course_code": "INT395",
            "course_title": "Supervised Learning",
            "academic_session": "2026–2027",
            "group_number": "12",
            "team_members": ["Kabya Varun", "Duggisetty Vasavi Vignan", "Shivraj Singh"]
        }
        
    # 5. Error Handlers
    @app.errorhandler(404)
    def not_found_error(error):
        if request.path.startswith("/api/"):
            return jsonify({"status": "error", "message": "API endpoint not found"}), 404
        return render_template("overview.html", active_page="overview"), 404

    @app.errorhandler(500)
    def internal_error(error):
        if request.path.startswith("/api/"):
            return jsonify({"status": "error", "message": "Internal server error"}), 500
        return render_template("overview.html", active_page="overview"), 500

    return app
