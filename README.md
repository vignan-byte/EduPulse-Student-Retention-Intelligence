# EduPulse v11.0 — Student Retention Intelligence System
### Course: INT395 — Supervised Learning | Academic Session: 2026–2027 | Group: 12
**Team Members:**
- Kabya Varun
- Duggisetty Vasavi Vignan
- Shivraj Singh

---

## 🌟 Executive Summary

**EduPulse v11.0** is an enterprise-grade, industry-standard educational analytics and student retention platform built on **Python 3.10 and Flask 3.1**, completely migrating away from ordinary prototyping tools to deliver a responsive, production-ready web application with a modern dark SaaS aesthetic.

The platform provides university academic leaders and advisors with calibrated machine learning predictions, explainable AI (SHAP & LIME), interactive counterfactual "Digital Twin" simulation, a role-governed SQLite CRM with PBKDF2 password hashing, and a 9-stage faculty demonstration mode.

---

## 🚀 Key Architectural Highlights

- **Pure Flask Architecture:** High-performance, WSGI-compliant web application utilizing modular Blueprints (`app.routes`, `app.api`), custom Jinja2 templates, Bootstrap 5, and Plotly.js.
- **Production WSGI Serving:** Natively supports both standard Flask development server and high-concurrency production serving via **Waitress**.
- **Zero-Leakage Decision Horizon:** Model evaluates student indicators strictly **After Semester 1**, completely isolating future post-intervention data (Semester 2 completions, graduation records) to guarantee authentic early discovery.
- **Calibrated Multi-Class Supervised Learning:** 3-class target mapping (`Dropout`, `Enrolled`, `Graduate`) calibrated with Platt/Sigmoid scaling (`CalibratedClassifierCV`), achieving an empirical **Test Accuracy of 77.29%** and **Macro F1 of 69.31%**.
- **Cost-Sensitive Screening Threshold:** Optimized screening threshold at **$\tau = 0.38$** (38.0%), elevating dropout detection recall to **76.8%** (compared to 71.1% at the standard 0.50 threshold).
- **Explainable AI (XAI):** Mathematically rigorous local feature attribution using permutation **SHAP** (with verified additivity error $< 10^{-5}$) and **LIME** local surrogate decision rules.
- **Digital Twin What-If Studio:** Non-causal counterfactual scenario modeling allowing advisors to simulate academic remediation and fee resolutions with instant risk delta calculation and algorithmic recourse milestones.
- **Advisor CRM & Audit Trail:** Local SQLite database with PBKDF2 password hashing (310,000 iterations), role-based access control (Admin vs. Advisor), structured follow-ups, and immutable audit logs.
- **Publication-Grade PDF Reporting:** Direct binary generation of formal Academic Retention Dossiers via **ReportLab**.
- **Continuous MLOps Reliability:** Live SHA-256 cryptographic manifest verification, automated 50-iteration latency benchmarking ($< 2.0$ ms per inference), and two-sample Kolmogorov-Smirnov (KS) & Population Stability Index (PSI) covariate drift detection.

---

## 📂 Repository Directory Structure

```text
Student_Retention_Intelligence_Final_Release/
├── app.py                          # Flask entrypoint (CLI support for --waitress, --port)
├── wsgi.py                         # WSGI production server hook
├── config.py                       # Centralized configuration (dev, test, prod)
├── requirements.txt                # Production dependency specification
├── app/
│   ├── __init__.py                 # Application factory (create_app)
│   ├── extensions.py               # ModelManager singleton & SQLite database initialization
│   ├── services/                   # Decoupled business logic services
│   │   ├── model_service.py        # ML artifacts, metrics, and dataset queries
│   │   ├── prediction_service.py   # Single student inference & cohort CSV batch screening
│   │   ├── simulation_service.py   # Digital Twin counterfactual modeling & recourse
│   │   ├── explanation_service.py  # Cached permutation SHAP & LIME generation
│   │   ├── monitoring_service.py   # Health diagnostics, SHA-256 integrity, & KS/PSI drift
│   │   ├── case_service.py         # Advisor CRM casework & audit history
│   │   └── report_service.py       # Formal dossier generation (Markdown & PDF)
│   ├── routes/                     # Jinja2 web page routes (11 modules)
│   │   ├── __init__.py
│   │   └── main.py                 # Page render blueprints
│   ├── api/                        # REST API endpoints
│   │   ├── __init__.py
│   │   ├── predict.py              # /api/predict/single, /api/predict/cohort
│   │   ├── simulate.py             # /api/simulate
│   │   ├── explain.py              # /api/explain/shap, /api/explain/lime
│   │   ├── analytics.py            # /api/analytics/threshold, /heatmap, /capacity
│   │   ├── cases.py                # /api/cases (Auth, CRUD, Audit, Followups)
│   │   ├── reports.py              # /api/reports/pdf, /api/reports/markdown
│   │   └── health.py               # /api/health, /api/health/drift
│   ├── templates/                  # Modern Jinja2 templates (Dark SaaS Aesthetic)
│   │   ├── base.html               # Master layout with collapsible sidebar & topbar
│   │   ├── overview.html           # Module 1: Executive Retention Dashboard
│   │   ├── student_risk.html       # Module 2: Student Risk Intelligence & CSV Batch Upload
│   │   ├── assessment.html         # Module 3: Digital Twin Studio & Recourse
│   │   ├── model_performance.html  # Module 4: 8-Model Benchmark & Threshold Simulator
│   │   ├── explainability.html     # Module 5: SHAP & LIME XAI Studio
│   │   ├── intervention.html       # Module 6: Intervention Planning CRM & Audit Trail
│   │   ├── cohort.html             # Module 7: Cohort Intelligence & Risk Heatmap
│   │   ├── institutional.html      # Module 8: Caseload Capacity & Tuition ROI Planner
│   │   ├── reliability.html        # Module 9: Model Reliability & Data Drift Monitor
│   │   ├── methodology.html        # Module 10: Methodology & Ethical Retention Charter
│   │   └── faculty_demo.html       # Module 11: 9-Stage Guided Faculty Demonstration
│   └── static/
│       ├── css/
│       │   ├── design-system.css   # Enterprise Navy/Charcoal Design System
│       │   └── dashboard.css       # Page components, confusion matrix, & stepper
│       └── js/
│           ├── app.js              # Session state, modal management, Plotly defaults
│           ├── prediction.js       # Live inference & CSV cohort processing
│           ├── simulation.js       # Digital twin slider interactions & PDF export
│           └── faculty-demo.js     # 9-stage guided walkthrough orchestration
├── src/                            # Pure Python ML & Analytics Core Engine
│   ├── ml.py                       # Supervised pipeline, training, cross-validation
│   ├── train.py                    # Multi-model benchmarking script
│   ├── explain.py                  # Permutation SHAP and LIME implementations
│   ├── intelligence.py             # Capacity planner, heatmaps, recourse, ReportLab PDF
│   ├── case_store.py               # DemoCaseStore with PBKDF2 hashing
│   ├── registry.py                 # Verified loading & SimpleImputer cross-version hook
│   ├── monitor.py                  # Two-sample KS test & Population Stability Index (PSI)
│   ├── safety.py                   # Anonymous CSV input validation & boundary checks
│   └── external_eval.py            # Bootstrap macro-F1 confidence intervals
├── artifacts/                      # Serialized ML artifacts
│   ├── model.joblib                # Fitted CalibratedClassifierCV model bundle
│   ├── metrics.json                # Complete benchmark metrics and curve data
│   └── manifest.json               # SHA-256 cryptographic signatures
├── data/
│   ├── students.csv                # Primary reference dataset (4,424 records)
│   └── independent_cohort.csv      # Independent validation cohort for drift testing
└── tests/                          # Automated Pytest Suite (75/75 passing)
    ├── test_flask_app.py           # All 11 web routes and template rendering tests
    ├── test_api_endpoints.py       # REST API endpoint verification
    ├── test_ui_apptest.py          # UI view stability & student 130 loading tests
    ├── test_ml.py                  # Pipeline, class ordering, feature staging
    ├── test_model_compatibility.py # Imputer compatibility & SHAP regression
    ├── test_case_store.py          # PBKDF2 hashing & RBAC permission checks
    ├── test_dataset.py             # Dataset schema & target sanitization
    ├── test_external_eval.py       # Bootstrap intervals & cohort evaluation
    ├── test_intelligence_advanced.py# Recourse, planner, heatmaps, PDF generation
    ├── test_monitor.py             # Covariate shift & drift detection
    ├── test_registry.py            # Manifest verification & missing artifact handling
    ├── test_safety.py              # Identity column rejection & injection prevention
    └── test_final.py               # Comprehensive system integration tests
```

---

## ⚡ Quick Start Guide

### 1. Prerequisites
- Python 3.10+ (tested on Python 3.10.11)
- Windows / macOS / Linux

### 2. Installation
Clone the repository and install the production dependencies:
```bash
pip install -r requirements.txt
```

### 3. Run the Flask Web Application
To start the standard development server:
```bash
python app.py
```
To run using the production **Waitress** WSGI server:
```bash
python app.py --waitress
```
Access the application in your browser at:
👉 **`http://127.0.0.1:5000/`**

---

## 🧪 Automated Testing Suite

The project includes an exhaustive automated test suite consisting of **75 unit, integration, security, and UI tests**:
```bash
python -m pytest tests/ -v
```
**Results:** `75 passed in ~25s` (100% pass rate).

---

## 🔐 Demonstration Credentials

To evaluate the Advisor CRM and Audit Trail:
- **Administrator:** `admin` / `Admin12345678!`
- **Academic Advisor:** `advisor1` / `Advisor12345678!`

---

## 📜 Ethical Governance & Non-Punitive Mandate

1. **Non-Deterministic Guidance:** Model predictions represent historical probabilities, not deterministic destiny.
2. **Voluntary Interventions:** All retention offers are student-centered, voluntary opportunities for academic tutoring and financial aid referrals.
3. **Strictly Non-Punitive:** Model outputs may never be used to revoke aid, block registration, or penalize students.
4. **Algorithmic Recourse:** Every flagged profile includes clear, achievable milestones showing how academic improvements reduce predicted risk.
