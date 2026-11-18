# Upgrade Changelog & Engineering Record

**Student Retention Intelligence — Tier-1 SaaS Transformation**  
*Course: INT395 Supervised Learning • Group 12*

---

## [v11.0.0] — Complete Streamlit to Flask Enterprise Migration (Current)

### 🚀 1. Complete Architectural Migration from Streamlit to Flask
- **Full MVC / Service Architecture:** Migrated the entire application from Streamlit to Flask 3.1, eliminating all Streamlit runtime dependencies, WebSocket coupling, and full-script reruns.
- **Blueprint Modularization:** Separated page rendering routes (`app.routes.main`) and REST API endpoints (`app.api.*`) into independent, reusable modules.
- **WSGI Concurrency Support:** Integrated `waitress` (v3.0.2) multi-threaded WSGI server alongside Flask development server. CLI execution supports `python app.py` or `python app.py --waitress --port 5000`.

### 🌐 2. Pure REST API Layer (12 Endpoints)
- **Prediction Services:** Added `/api/predict/single`, `/api/predict/cohort`, `/api/predict/archetypes`, and `/api/predict/student/<idx>`.
- **Digital Twin Simulation:** Added `/api/simulate` for real-time counterfactual what-if modeling with boundary validation and recourse milestones.
- **Explainability API:** Added `/api/explain/shap` and `/api/explain/lime` returning Plotly-compatible JSON payloads with in-memory feature hash caching.
- **Analytics & Decision Support:** Added `/api/analytics/threshold` (sub-millisecond confusion matrix calculation on 885 holdout records), `/api/analytics/heatmap`, and `/api/analytics/capacity`.
- **Advisor CRM:** Added `/api/cases` (session-checked CRUD, structured follow-ups, and admin audit trail).
- **Reports & Diagnostics:** Added `/api/reports/pdf`, `/api/reports/markdown`, `/api/health`, and `/api/health/drift`.

### 🎨 3. Enterprise Dark SaaS Frontend System
- **Design System (`design-system.css`):** Built cohesive CSS variables defining a deep space navy/charcoal theme (`#0B1020`, `#111827`, `#3B82F6`, `#06B6D4`), high-contrast text (`#F9FAFB`), custom scrollbars, and modern cards.
- **Collapsible Navigation & Sticky Header:** 11-module sidebar with active link indicators, INT395 Group 12 credentials, real-time model status pill, and advisor authentication modal.
- **Client-Side Plotly.js:** Replaced server-side chart rendering with native Plotly.js CDN rendering, enabling zero-latency zooming, hover tooltips, and interactive threshold updating.

### 🧪 4. Comprehensive Testing & Quality Assurance
- **75/75 Automated Tests Passing:** Created `tests/test_flask_app.py` and `tests/test_api_endpoints.py`, while updating `tests/test_ui_apptest.py` to test the Flask WSGI client. All tests pass with zero failures in ~25 seconds.
- **Zero Streamlit Remnants:** Verified that `src/` core Python modules contain zero Streamlit imports and function 100% independently.

---

## [v10.0.0] — Master Engineering Upgrade Release

### 🛠️ 1. Critical Compatibility & Pipeline Resilience
- **SimpleImputer Cross-Version Compatibility Hook (`src/registry.py`):** Implemented recursive inspection and attribute synchronization (`ensure_imputer_compatibility`), guaranteeing both `_fit_dtype` and `fill_dtype` are properly populated on all pipeline imputers. Resolves cross-version scikit-learn unpickling discrepancies (`AttributeError: 'SimpleImputer' object has no attribute 'fill_dtype'`).
- **Dependency Pinning:** Explicitly pinned compatible scikit-learn boundaries in `requirements.txt` (`scikit-learn>=1.3.0,<=1.7.2`).
- **Student Index 130 Regression Test (`tests/test_model_compatibility.py`):** Verified live model inference on historical index 130, ensuring finite probabilities summing to 1.0 without runtime exceptions.
- **Demo Personas Verification:** Validated live inference across all demonstration archetypes (High, Moderate, Low Risk).

### 🎨 2. Complete UI/UX & Visual System Overhaul
- **Elimination of White Header Strip:** Aligned `.streamlit/config.toml` to `base = "dark"` (`backgroundColor = "#0B1020"`, `secondaryBackgroundColor = "#111827"`, `textColor = "#F8FAFC"`) and injected CSS overrides for `[data-testid="stHeader"]` and `.stApp > header`, eliminating unwanted white bars.
- **KPI Card Truncation Fix:** Restructured the executive overview into two rows of 3 wide cards with word-wrapping and card min-height rules, completely eliminating truncated values (e.g. `280 (31.6...`).
- **WCAG AA Contrast Overhaul:** Darkened notification containers and alert backgrounds (error `#450A0A`, warning `#451A03`, info `#172554`, success `#064E3B`) with high-contrast text and glowing borders.
- **BaseWeb Select Dropdown Styling:** Styled selectbox popovers, listboxes, and options with dark backgrounds (`#111827`) and cyan highlights (`#38BDF8`), ensuring complete visual consistency.
- **Benchmark Table Readability:** Replaced technical abbreviations with readable descriptions (e.g. `cv_macro_f1_mean` $\to$ `CV Macro-F1 (Mean)`, `logistic` $\to$ `Balanced Logistic Regression (Selected Production Model)`).

### 🧬 3. Student Digital Twin & What-If Studio
- **Interactive Digital Twin Engine (`src/ui/views.py`):** Built a dedicated simulation panel allowing users to adjust first-semester approved credits, GPA, tuition status, debtor status, and scholarship standing.
- **Live Model Recalculation:** Re-runs the verified model pipeline in real-time, showing updated class probabilities, top predicted outcome, and risk deltas ($\Delta$ pp).
- **Realistic Range & Out-of-Distribution Validation:** Detects impossible inputs (e.g., approved credits exceeding enrolled credits) and alerts the user immediately.
- **Session Scenario History:** Enables advisors to save simulated scenarios into an expandable session history table for side-by-side comparison.
- **Non-Causal Disclosure:** Prominently states that simulated what-if associations reflect historical correlations and do not constitute guaranteed causal outcomes.

### 🎯 4. AI-Assisted Retention Recommendation Engine
- **Transparent Evidence-Linked Logic (`src/intelligence.py`):** Generates structured support recommendations with priority tiers (`Critical / Urgent`, `Moderate Priority`, `Advisory / Routine`), clear evidence triggers, rationale, and designated campus referral channels (Tutoring Center, Financial Aid, Counseling).
- **Advisor CRM Integration:** Connects recommendations to the case store for formal follow-up tracking.

### 🔬 5. Interactive Confusion Matrix & Threshold Lab
- **Dynamic Holdout Threshold Lab (`src/ui/views.py`):** Real-time slider ($\tau \in [0.10, 0.90]$) recalculating TP, FP, FN, TN, Recall, Precision, Specificity, and Balanced Accuracy on 885 held-out test students.
- **Live 2x2 Binary Confusion Matrix Heatmap:** Plotly visual heatmap updating dynamically with threshold adjustments.
- **Advisor Caseload Impact:** Models required advisor staffing based on flagged student counts ($\lceil \text{flagged}/50 \rceil$).

### 🗺️ 6. Student Cohort Intelligence & Risk Heatmap
- **Multidimensional Cohort Cross-Tabulation (`src/intelligence.py`):** Slices 4,424 students across academic completion bands, grade point averages, tuition standing, and scholarship equity.
- **Interactive Heatmap Visualizer:** Plotly heatmap annotated with empirical dropout rates and sample sizes ($N=\dots$), flagging cohorts with $N < 30$.
- **Ethical Safeguard Notice:** Emphasizes that group differences reflect systemic friction and preparation, prohibiting discriminatory tracking.

### 🛡️ 7. Model Reliability Center & Data Drift Monitor
- **Active Model Health Checks:** Displays SHA-256 pipeline checksum, calibration status, and real-time single-record inference latency (~1.2 ms/row).
- **Population Stability Index (PSI) Audit (`src/monitor.py`):** Calculates PSI and KS-distance between reference training data ($N=4,424$) and the independent validation cohort ($N=55$), color-coding drift severity.

### 📄 8. Publication-Grade PDF & Markdown Dossier Export
- **ReportLab Binary PDF Generator (`src/intelligence.py`):** Produces publication-grade PDF dossiers (`.pdf`) complete with case reference, risk badge, probability breakdown, student profile, evidence-linked actions, and counterfactual recourse.
- **Dual Export:** Downloadable directly from Student Assessment and Faculty Demo Stage 7 in both PDF and Markdown.

### 🎓 9. Nine-Stage Faculty Demo Mode 2.0
- **Pre-Demo Health Check & Readiness Banner:** Verifies model integrity, 8 benchmark architectures, dataset availability, and live inference before the defense begins (`Faculty Demo Readiness: 100% Operational`).
- **Instant Persona Inference:** Automatically runs inference upon selecting a persona in Stage 4 without requiring button clicks.
- **Full Viva Walkthrough:** Previous/Next/Restart controls covering Problem, Dataset, Benchmark, Inference, SHAP XAI, Digital Twin, Recommendations, Error Trade-offs, and Architecture.

### 🧪 10. Automated Testing Expansion
- **51 Automated Tests (100% Pass Rate):** Expanded test suite from 42 to **51 passing tests** covering model compatibility, SimpleImputer recovery, student 130 regression, cohort heatmap computation, and headless AppTest navigation.

#### 🎨 Premium UI/UX Redesign
- **Linear/Vercel Dark Theme Engine:** Implemented a full CSS dark design system (`src/ui/theme.py`) featuring `#0B1020` primary background, `#111827` sidebar, `#172033` card backgrounds, cyan/blue glowing accents, and high-contrast typography.
- **Persistent Sidebar Navigation Shell:** Transformed tab-heavy navigation into an intuitive 9-view left sidebar with product branding (`EduPulse Retention`), student group credentials, and active status indicators.
- **Plotly Dark Template Engine:** Replaced default white charts with custom dark-themed Plotly visualizations matching the enterprise palette with subtle gridlines and accessible contrast.
- **Interactive Before-and-After Sensitivity Card (`src/ui/components.py`):** Built a side-by-side comparative panel contrasting baseline student profiles against modified sensitivity scenarios with delta indicators ($\Delta$ pp).

#### 🎓 9-Stage Guided Faculty Demo Mode (`src/ui/demo_mode.py`)
- Created a dedicated presentation mode allowing a seamless 5–8 minute viva defense without navigating through disjointed sub-pages:
  - *Stage 1: Project Scope & Academic Problem* (INT395 Group 12 intro, problem framing).
  - *Stage 2: Dataset Exploration* (UCI 697 structure, class proportions, data leakage controls).
  - *Stage 3: 8-Algorithm Benchmark* (Model comparison, Macro-F1 selection rationale).
  - *Stage 4: Real-Time Risk Prediction* (3 verified demonstration personas: High, Moderate, Low risk; live AI inference).
  - *Stage 5: Explainable AI (SHAP)* (Live Shapley additive feature attribution with additivity check).
  - *Stage 6: What-If Sensitivity* (Interactive grade/approved credit adjustments with before-and-after deltas).
  - *Stage 7: Evidence-Linked Support* (Rule-based academic tutoring and financial aid referrals).
  - *Stage 8: Error Trade-offs* (Operational FP vs. FN analysis, sigmoid calibration benefits).
  - *Stage 9: Enterprise Architecture* (Full pipeline diagram, security boundaries, ethical charter).
- Added demo controls: `Next ➔`, `⬅ Previous`, `Restart ↺`, and stage progress tracking.

#### 🧠 Machine Learning & Advanced Diagnostics (`src/ml.py`)
- **Stacking Classifier (Super Learner):** Integrated an 8th model architecture combining Balanced Logistic Regression, Random Forest, and Gradient Boosting with an L2 meta-classifier.
- **Multiclass One-vs-Rest ROC Curves:** Added interactive Plotly ROC curves for Dropout (AUC 0.898), Graduate (AUC 0.885), and Enrolled (AUC 0.725), alongside chance baselines.
- **Precision-Recall Curves:** Added PR curves with Average Precision (AP) scores to evaluate performance on imbalanced classes.
- **Visual Reliability Diagram (Calibration Curve):** Visualized uncalibrated vs. calibrated probabilities against the 45° diagonal, validating Brier score reduction from 0.119 to 0.106.
- **Interactive Operational Threshold Simulator:** Added dynamic threshold adjustment recalculating holdout precision, recall, false alarms, and flags.

#### 🎯 Actionable Decision Support & XAI (`src/intelligence.py`, `src/explain.py`)
- **Algorithmic Counterfactual Recourse (`counterfactual_recourse`):** Created a prescription engine finding minimal actionable improvements (e.g. passing $\ge 2$ credits or clearing fee balance) to exit the review category.
- **Diverging Plotly XAI Charts:** Built color-coded bar charts for SHAP and LIME (Crimson for risk factors, Emerald for protective factors).
- **Institutional Capacity & ROI Simulator (`advisor_capacity_planner`):** Simulates advisor caseload bandwidth constraints and calculates modeled tuition preservation.
- **Printable Executive Retention Dossier:** Single-click export of publication-grade PDF dossiers (`generate_student_dossier_pdf` via ReportLab) and formal markdown briefs (`generate_student_dossier`), complete with multi-class probabilities, student profile, evidence-linked actions, and counterfactual recourse.

#### 🧪 Testing, Quality Assurance & Security
- **Test Suite Expansion:** Added [tests/test_intelligence_advanced.py](file:///C:/Users/duggi/OneDrive\Desktop/Student_Retention_Intelligence_Final_Release%20(2)/tests/test_intelligence_advanced.py), raising total automated tests from 37 to **43 tests (100% pass rate)**.
- **Streamlit AppTest Smoke Suite (`scripts/smoke_app.py`):** Verified headless execution with zero exceptions and updated modern Streamlit layout APIs (`width="stretch"`).
- **Bundled Independent Cohort (`data/independent_cohort.csv`):** Validated using `src/external_eval.py` and `src/monitor.py`.
- **Pre-Seeded Demo Accounts:** Initialized `local_demo/cases.sqlite3` with `admin` (`AdminPass12345!`) and `advisor1` (`AdvisorPass12345!`).
- **Cryptographic Release Manifest:** Maintained SHA-256 integrity validation in `RELEASE_MANIFEST.json` and bundled clean standalone distributable `Student_Retention_Intelligence_Professional_Upgrade.zip` (0.28 MB, 82 files).
