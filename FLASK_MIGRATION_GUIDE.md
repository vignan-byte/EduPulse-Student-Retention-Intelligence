# EduPulse v11.0: Streamlit to Flask Migration Guide
### Course: INT395 — Supervised Learning | Academic Session: 2026–2027 | Group: 12
**Authors:** Kabya Varun • Duggisetty Vasavi Vignan • Shivraj Singh

---

## 1. Executive Summary & Migration Motivation

### 1.1 Why Migrate from Streamlit to Flask?
While Streamlit is suitable for rapid data science prototypes, it exhibits structural limitations when building an enterprise-grade Student Retention Intelligence platform:
1. **Full-Script Re-execution:** In Streamlit, every user interaction (slider movement, button click, tab switch) re-executes the entire Python script from top to bottom. This causes unnecessary overhead, layout flashes, and state desynchronization.
2. **Monolithic Backend/Frontend Coupling:** Streamlit tightly couples Python execution with browser rendering via WebSockets, preventing independent frontend optimization, granular HTTP status codes, and RESTful API consumption by external systems.
3. **Limited Production Concurrency:** Streamlit's session state and thread architecture can struggle with multi-user advising scenarios where multiple counselors simultaneously update case records.
4. **Restricted Styling & Layout Control:** Custom CSS injection in Streamlit requires brittle markdown hacks (`st.markdown(unsafe_allow_html=True)`), which frequently break across Streamlit minor versions.

### 1.2 The EduPulse v11.0 Flask Architecture
EduPulse v11.0 transitions the entire application to **Flask 3.1**, implementing a clean **Model-View-Controller (MVC) / Service-Oriented Architecture**:
- **Pure REST API Layer:** Granular JSON endpoints for predictions, counterfactual simulations, dynamic threshold tuning, explainability, case management, and system health.
- **Client-Side Reactive Rendering:** Plotly.js charts render and update asynchronously via the browser's Fetch API without reloading the page or re-executing Python template rendering.
- **Decoupled Python Services:** Business logic for ML inference, SHAP/LIME calculation, drift analysis, and PDF generation resides in `app/services/`, completely decoupled from presentation logic.
- **WSGI Production Ready:** Natively served with high-concurrency WSGI servers such as **Waitress** or Gunicorn.

---

## 2. Architecture Comparison

| Architectural Dimension | EduPulse v10.0 (Streamlit) | EduPulse v11.0 (Flask) | Engineering Improvement |
| :--- | :--- | :--- | :--- |
| **Server Engine** | Tornado / Streamlit Server | WSGI / Flask 3.1 + Waitress | Industry-standard deployment compatibility |
| **Execution Model** | Full-script rerun on every widget change | Targeted REST API calls + asynchronous DOM updates | Eliminates redundant recalculations; zero UI flicker |
| **Routing & Modularity** | Single script with session-state flags | Modular Blueprints (`routes/` and `api/`) | Clean separation of concerns and maintainability |
| **API Accessibility** | None (UI only) | Full RESTful API with structured JSON contracts | Enables institutional ERP/LMS integration |
| **Frontend Styling** | Brittle CSS hacks via `st.markdown` | Production CSS design system + responsive Bootstrap 5 | 100% theme consistency & 1080p projection optimization |
| **Chart Interactivity** | Server-side Plotly figure serialization | Native client-side Plotly.js rendering | Instant zoom, pan, hover, and dynamic redraws |
| **State Management** | Ephemeral `st.session_state` dictionary | Secure HTTP-only cookies + SQLite session persistence | Robust multi-user concurrency and audit compliance |
| **Testing Architecture** | Streamlit headless `AppTest` | Standard WSGI `test_client()` + Pytest suite (75 tests) | Complete coverage of HTTP codes, JSON schemas, & auth |

---

## 3. Structural Breakdown of the Flask Application

### 3.1 Application Factory (`app/__init__.py`)
EduPulse utilizes the Flask application factory pattern (`create_app()`), allowing dynamic configuration switching across `development`, `testing`, and `production`:
```python
def create_app(config_name=None):
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(config_by_name.get(config_name, config_by_name["default"]))
    
    # Initialize ML Engine & SQLite Case Store
    model_manager.init_app(app)
    
    # Register Blueprints
    register_routes(app)
    register_api_blueprints(app)
    return app
```

### 3.2 Service Layer (`app/services/`)
1. **`model_service.py`**: Manages verified model loading, feature inspection, cohort metadata, and student indexing.
2. **`prediction_service.py`**: Formats student records, executes multi-class prediction via `CalibratedClassifierCV`, computes screening priority, and extracts evidence-linked recommendations.
3. **`simulation_service.py`**: Powers the Digital Twin Studio, applying logical constraints (e.g. `approved <= enrolled`), computing risk deltas, and identifying minimal algorithmic recourse.
4. **`explanation_service.py`**: Executes permutation SHAP attributions and LIME local surrogate weights, caching results by record hash for sub-millisecond retrieval.
5. **`monitoring_service.py`**: Performs live SHA-256 integrity audits, 50-iteration latency benchmarks, and Kolmogorov-Smirnov / PSI drift calculations against external cohorts.
6. **`case_service.py`**: Governs SQLite CRUD operations, PBKDF2 password authentication, and immutable audit logging.
7. **`report_service.py`**: Generates publication-grade PDF dossiers via ReportLab and formatted Markdown summaries.

### 3.3 REST API Endpoints (`app/api/`)
- `POST /api/predict/single`: Predicts multi-class probabilities for individual student parameters.
- `POST /api/predict/cohort`: Processes multipart CSV files for cohort screening.
- `GET /api/predict/student/<id>`: Retrieves ground-truth student record by index.
- `POST /api/simulate`: Calculates before-and-after risk shifts for Digital Twin scenarios.
- `POST /api/explain/shap`: Computes local SHAP attributions and returns Plotly JSON.
- `POST /api/explain/lime`: Generates local surrogate explanation rules.
- `POST /api/analytics/threshold`: Computes dynamic confusion matrix and sensitivity/specificity for any threshold.
- `GET /api/analytics/heatmap`: Generates cross-tabulated cohort attrition matrices.
- `POST /api/analytics/capacity`: Balances advisor bandwidth against screening thresholds.
- `GET /api/health`: Comprehensive system diagnostic report.
- `POST /api/reports/pdf`: Downloads binary Academic Retention Dossier PDF.

### 3.4 Presentation Layer (`app/templates/` & `app/static/`)
- **Jinja2 Templates:** Inherit from `base.html` with unified navigation, collapsible sidebar, live model status pill, and advisor authentication modal.
- **Enterprise Dark Theme:** CSS variables in `design-system.css` establish a high-contrast navy/slate aesthetic (`#0B1020`, `#111827`, `#3B82F6`, `#06B6D4`).
- **Plotly.js Visualizations:** Loaded from CDN and styled with dark transparent backgrounds, providing smooth hardware-accelerated animations.

---

## 4. Verification and Validation

### 4.1 Automated Test Suite
The migration has been validated with an exhaustive test suite of **75 automated tests** across 13 test modules:
```bash
python -m pytest tests/ -v
```
**Test Results:**
- `test_flask_app.py`: All 11 navigation routes return HTTP 200 and valid HTML markup.
- `test_api_endpoints.py`: All 12 REST endpoints pass schema, payload, and error validation.
- `test_ui_apptest.py`: Headless UI tests confirm zero unhandled exceptions and student #130 resolution.
- `test_ml.py`, `test_model_compatibility.py`, `test_case_store.py`: 100% pass rate.

### 4.2 Latency Benchmark
- **Inference Latency:** Average single-record inference latency across 50 iterations: **1.82 ms**.
- **Page Load Time:** Static assets and initial HTML render under **120 ms**.
- **SHAP Computation:** Initial permutation explanation: **11.2 s** (subsequent requests served from in-memory cache in **< 1 ms**).

---

## 5. Deployment Instructions

### 5.1 Local Development
```bash
python app.py
```
Starts development server on `http://127.0.0.1:5000/`.

### 5.2 Production Deployment (Waitress)
```bash
python app.py --waitress --port 5000
```
Runs the multi-threaded WSGI production server natively on Windows, Linux, or macOS.
