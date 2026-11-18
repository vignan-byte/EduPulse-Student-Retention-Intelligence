# Student Dropout Risk & Retention Intelligence System

**INT395 — Supervised Learning | Group 12 | 2026–27**

An explainable educational ML research prototype using the real **UCI 697: Predict Students' Dropout and Academic Success** dataset. It compares multiclass prediction models at three prediction points: enrollment, first-semester end, and second-semester end.

## Quick start (Python 3.10+)

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python -m src.train --download --stage "After semester 1"
streamlit run app.py
pytest -q
```

The first training command downloads public data from the official UCI archive into `data/students.csv`. If your network blocks the archive, download `data.csv` from [UCI dataset 697](https://archive.ics.uci.edu/dataset/697/predict+students+dropout+and+academic+success), rename it `students.csv`, and place it in `data/`; then omit `--download`.

Other experiments:

```bash
python -m src.train --stage "Admission" --output artifacts/admission
python -m src.train --stage "After semester 2" --output artifacts/semester2
python -m src.train --stage "After semester 1" --tune
python -m src.train --stage "After semester 1" --full-benchmark --output artifacts/full
python -m src.monitor --reference data/students.csv --candidate another_authorized_anonymous_dataset.csv --output drift_report.json
```

The dashboard currently loads only the top-level `artifacts/model.joblib` and `artifacts/metrics.json`; use default output to replace its displayed model. Outputs are **real measurements only after running training**, not prefilled results.

## Implemented

- Input schema/label validation and official source loading
- Prediction-time feature restrictions to reduce future-semester leakage
- Categorical one-hot encoding, numeric imputation and scaling inside fitted pipelines
- Logistic Regression, Random Forest and Gradient Boosting comparisons
- Stratified 80/20 split, five-fold CV, macro-F1 selection and held-out metrics
- Optional randomized hyperparameter search for Random Forest
- Accuracy, balanced accuracy, per-class metrics, macro/weighted F1, log loss, one-vs-rest ROC-AUC, confusion matrix
- Model save/load, single-row prediction, Streamlit overview, model evaluation, student assessment and global permutation importance
- Optional full benchmarking: Decision Tree, KNN, SVM, Naive Bayes in addition to baseline algorithms
- Retrospective dropout screening diagnostics: precision, recall, false positive/negative counts, threshold comparisons, Brier score and 10-bin calibration error
- Review threshold chosen exclusively from cross-validated out-of-fold training predictions, then evaluated on held-out data
- Optional training-only sigmoid probability calibration (`--no-calibration` for an uncalibrated baseline), with Brier score before/after comparison
- Dataset fingerprint and environment version metadata saved with evaluation metrics
- V6 SHA-256 local model-artifact manifest verified before deserialization (integrity, not publisher authentication)
- Offline exploratory feature-shift report with KS and categorical-distribution distances
- GitHub Actions test workflow (included, but remote execution not verified)
- V7 local, fictional-case SQLite workflow with password-hashed users, advisor ownership checks, admin audit inspection and case deletion
- V8 independent labeled-cohort evaluation CLI with bootstrap macro-F1 confidence interval (requires truly separate data)
- V8 subgroup reporting suppresses groups with insufficient positive or negative examples
- Dockerfile for local container demo and CI workflow with model training + dashboard smoke check (Docker/remote CI execution not verified here)
- Exploratory subgroup slices for Gender, Scholarship holder and Displaced with small sample suppression
- Fictional-case advisor support review in browser-session memory (no identity management or persistent student case store)
- Unit tests for stage leakage and prediction input validation

## Next milestones (not yet implemented)

- Thorough compatibility and runtime validation of the optional per-record SHAP and LIME dashboard tools
- Calibrated probabilities and intervention threshold selection
- Subgroup fairness audits, temporal/external validation, operational access controls
- Stacking, Bayesian optimization, nested cross-validation, statistically principled threshold selection
- Authenticated advisor feedback workflow with persistent privacy-aware audit trail

## Explanation tab

The Explainability page includes optional **SHAP** (model-agnostic permutation) and **LIME** (surrogate on encoded inputs) for one selected historical row. Install both dependencies from `requirements.txt`. Both were smoke-tested manually against a trained Random Forest and actual UCI record; they are not yet covered by full automated numerical consistency tests. SHAP may run slowly. Features shown by LIME are encoded model features, while SHAP reports original input features. Neither method shows causation.

## Screening and calibration

The model is trained for three mutually exclusive labels; the supplementary screening table treats Dropout as positive for retrospective review only. It does **not** claim that a currently Enrolled person will never drop out. Threshold scenarios are descriptive on the held-out set, not approved operational thresholds. Do not select a threshold after seeing test results without creating a new untouched evaluation set.

The subgroup audit is exploratory. Small cells are suppressed but this is not an anonymization or fairness guarantee. The public dataset is not representative of every institution. The application has **no authentication**, and is intended for localhost demonstrations with public dataset records only.

**V6 artifact checks:** Training creates `artifacts/manifest.json`, hashing the model and metrics. The app rejects changed or missing artifacts. This is not a digital signature; a malicious publisher could replace the manifest too. Never load untrusted joblib/pickle files.

**V6 drift checks:** `python -m src.monitor` compares two governed feature tables (at least 30 records each). The report is exploratory, not a production alerting service.

## V8 validation and deployment tools

For an institution-approved, **independent** labeled cohort with identical feature names:

```powershell
.\.venv\Scripts\python.exe -m src.external_eval --model-dir artifacts --cohort independent_cohort.csv --output external_validation.json
```

This reports holdout metrics and a bootstrap macro-F1 interval. Reusing the training or UCI test records does **not** count as external validation. No independent institutional dataset has been evaluated in this project.

The Dockerfile can build and run the public-data demonstration, training a model during image build. If Docker is installed, run `docker build -t retention-demo .` and `docker run --rm -p 8501:8501 retention-demo`. The container is a local demo only, not a secure public deployment. Container build and live hosted deployment were not verified in this release environment.

## V7 Advisor demo setup (fictional records only)

Create the first local administrator, then an advisor; the CLI prompts for passwords rather than storing defaults:

```powershell
.\.venv\Scripts\python.exe -m scripts.create_demo_user --username admin --role admin
.\.venv\Scripts\python.exe -m scripts.create_demo_user --username advisor1 --role advisor --actor admin
```

Open the Streamlit `Support Review` tab and sign in. Advisor accounts see only their assigned fictional cases. An admin can inspect the local audit log and reassign cases. Deletion removes the case but keeps a minimal audit event. All records require `DEMO-` IDs and predefined support options.

**Security warning:** This is an offline educational access-control demonstration, not a production identity system. It has no MFA, external identity provider, server-wide rate limiting, secure hosted session layer, encryption at rest or validated privacy governance. Do not use real student records, and do not publish the local SQLite database.

## Faculty demo edition

The presentation file `Student_Retention_Intelligence_Presentation.pptx`, `PRESENTATION_GUIDE.md`, and `MODEL_CARD.md` summarize the measured results and a safe demonstration flow. The source ZIP includes the published UCI CSV in `data/students.csv`, allowing offline training without `--download` (the UCI repository remains the attribution source).

Recommended Windows commands from the extracted project root:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m src.train --full-benchmark
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m streamlit run app.py
```

The presentation reports the measured benchmark numbers, which may vary slightly with library versions. Re-run the training and retain your own logs for assessment.

## Local support-review prototype

The Support Review tab accepts only references beginning `DEMO-`; entries live in Streamlit session memory and can be exported manually. It is for illustrating advisor workflows, not real case management. Do not input names, roll numbers, personal circumstances, or sensitive student information. There is no access control, durable storage, deletion workflow, or multiuser concurrency protection.

Single-row uploads have a 250 KB parser limit, a one-row restriction and an obvious-identity-column filter. These checks do **not** make uploaded data anonymous or authorize real student-data use.

## Threshold policy

During training, out-of-fold predictions on the training portion are used to propose a dropout screening threshold targeting at least 75% positive predictive value. The operating point is then tested on the held-out 20%. This avoids picking a threshold directly from the final test results, but it is **not** calibrated probability estimation, external validation, or institutional authorization to act on a score.

## Responsible use

Research/teaching prototype only. **Never** treat predicted outcome as certainty or use it for exclusion, penalties, or automatic intervention. The published dataset has no individual attendance-percentage column. Do not relabel *Enrolled* as a guaranteed future non-dropout. Data represents an institution-specific historical population; independent validation is necessary before any real deployment. Do not upload student-identifying data to a public Streamlit service.

Saved joblib artifacts must be loaded only from trusted training runs because they can execute code when deserialized.

## Source

UCI ML Repository, dataset 697: https://archive.ics.uci.edu/dataset/697/predict+students+dropout+and+academic+success
