"""Headless Streamlit integration smoke test with a trained, verified model."""
from pathlib import Path
from streamlit.testing.v1 import AppTest
from src.registry import verified_load


def main():
    for filename in ("model.joblib", "metrics.json", "manifest.json"):
        if not (Path("artifacts") / filename).exists():
            raise SystemExit(f"Missing trained artifact: {filename}")
    verified_load("artifacts")
    app_file = Path(__file__).resolve().parents[1] / "app.py"
    app = AppTest.from_file(str(app_file), default_timeout=35).run()
    if app.exception:
        raise SystemExit(f"Streamlit exception: {app.exception[0].message}")
    if not any("Student Dropout" in item.value for item in app.title):
        raise SystemExit("Dashboard title missing")
    historical = next(c for c in app.checkbox if "Use one existing" in c.label)
    historical.check().run()
    if app.exception:
        raise SystemExit(f"Assessment exception: {app.exception[0].message}")
    if not any("Estimated dropout" in m.label for m in app.metric):
        raise SystemExit("Assessment probability missing")
    print("Final dashboard and historical student assessment smoke passed")


if __name__ == "__main__":
    main()
