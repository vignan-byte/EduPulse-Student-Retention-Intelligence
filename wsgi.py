"""WSGI Application Entry Point for Production Deployments."""
import os
from app import create_app

application = create_app()
app = application  # Alias for compatibility with gunicorn wsgi:app or gunicorn app:app

if __name__ == "__main__":
    from waitress import serve
    port = int(os.environ.get("PORT", 5000))
    host = "0.0.0.0" if os.environ.get("PORT") else "127.0.0.1"
    serve(application, host=host, port=port)
