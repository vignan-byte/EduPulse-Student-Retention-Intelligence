"""EduPulse Flask Application Root Entry Point."""
import argparse
import sys
from app import create_app

app = create_app()

def main():
    parser = argparse.ArgumentParser(description="Run the EduPulse Flask Web Application")
    parser.add_argument("--host", default="127.0.0.1", help="Host interface to bind (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=5000, help="Port to listen on (default: 5000)")
    parser.add_argument("--waitress", action="store_true", help="Serve using production Waitress WSGI server")
    parser.add_argument("--debug", action="store_true", help="Run with debug reloading enabled")
    args = parser.parse_args()

    print(f"============================================================")
    print(f" EduPulse Student Retention Intelligence System v11.0 (Flask)")
    print(f" Course: INT395 Supervised Learning | Group 12 (2026–2027)")
    print(f" Authors: Kabya Varun • Duggisetty Vasavi Vignan • Shivraj Singh")
    print(f" Access UI: http://{args.host}:{args.port}/")
    print(f"============================================================")

    if args.waitress:
        try:
            from waitress import serve
            print(f"[Waitress] Serving on http://{args.host}:{args.port}")
            serve(app, host=args.host, port=args.port)
        except ImportError:
            print("[Warning] Waitress not installed; falling back to Flask development server.")
            app.run(host=args.host, port=args.port, debug=args.debug)
    else:
        app.run(host=args.host, port=args.port, debug=args.debug)

if __name__ == "__main__":
    main()
