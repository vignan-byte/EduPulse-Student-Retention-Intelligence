"""WSGI Application Entry Point for Production Deployments."""
from app import create_app

application = create_app()

if __name__ == "__main__":
    from waitress import serve
    serve(application, host="127.0.0.1", port=5000)
