# EduPulse v11.0: REST API Specification
### Course: INT395 — Supervised Learning | Academic Session: 2026–2027 | Group: 12

This document provides complete technical specifications for the EduPulse REST API layer. All endpoints consume and return `application/json` unless noted otherwise.

---

## 1. Prediction Endpoints

### 1.1 Single Student Risk Evaluation
- **URL:** `/api/predict/single`
- **Method:** `POST`
- **Description:** Evaluates a single student record against the calibrated machine learning pipeline and screening threshold.
- **Request Body:**
```json
{
  "student": {
    "Curricular units 1st sem (enrolled)": 6.0,
    "Curricular units 1st sem (approved)": 1.0,
    "Curricular units 1st sem (grade)": 10.2,
    "Admission grade": 115.0,
    "Age at enrollment": 21,
    "Debtor": 1,
    "Tuition fees up to date": 0,
    "Scholarship holder": 0
  },
  "threshold": 0.38
}
```
- **Response (200 OK):**
```json
{
  "status": "success",
  "probabilities": {
    "Dropout": 0.6421,
    "Enrolled": 0.2212,
    "Graduate": 0.1367
  },
  "dropout_probability": 0.6421,
  "screening_threshold": 0.38,
  "is_screened": true,
  "risk_tier": "High Risk",
  "review_priority": "Advisor review",
  "badge_color": "danger",
  "top_predicted_outcome": "Dropout",
  "top_class_confidence": 0.6421,
  "uncertain_prediction": false,
  "recommendations": [
    {
      "category": "Academic Intervention",
      "priority": "Critical / Urgent",
      "evidence": "1st semester: 1/6 units approved",
      "rationale": "Credit completion below 50% is the single strongest empirical leading indicator of dropout risk.",
      "action": "Advisor: discuss course workload and offer subject tutoring; review progress in 14 days.",
      "referral_channel": "Campus Academic Tutoring & Course-Planning Center"
    }
  ],
  "features": { ... }
}
```

### 1.2 Preset Archetypes Lookup
- **URL:** `/api/predict/archetypes`
- **Method:** `GET`
- **Description:** Returns pre-configured student demonstration personas.
- **Response (200 OK):**
```json
{
  "status": "success",
  "archetypes": {
    "High Risk (Academic Difficulty & Tuition Arrears)": { ... },
    "Borderline Risk (Low Approved Credits)": { ... },
    "Low Risk / Dean's List (Scholarship Holder)": { ... }
  }
}
```

### 1.3 Ground-Truth Student Record by Index
- **URL:** `/api/predict/student/<int:idx>`
- **Method:** `GET`
- **Description:** Retrieves raw student features from the reference dataset by row index (0–4423).
- **Response (200 OK):**
```json
{
  "status": "success",
  "index": 130,
  "student": { ... }
}
```

### 1.4 Batch Cohort CSV Screening
- **URL:** `/api/predict/cohort`
- **Method:** `POST`
- **Content-Type:** `multipart/form-data`
- **Parameters:**
  - `file`: CSV file containing student feature columns
  - `threshold`: Optional screening threshold float (e.g. `0.38`)
- **Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "total_records": 100,
    "screening_threshold": 0.38,
    "flagged_count": 32,
    "flagged_percentage": 32.0,
    "average_risk": 0.354,
    "results_sample": [ ... ]
  }
}
```

---

## 2. Digital Twin Simulation Endpoint

### 2.1 Counterfactual What-If Simulation
- **URL:** `/api/simulate`
- **Method:** `POST`
- **Description:** Computes side-by-side risk deltas between baseline and modified profiles, enforcing domain constraints and calculating algorithmic recourse milestones.
- **Request Body:**
```json
{
  "baseline": {
    "Curricular units 1st sem (enrolled)": 6.0,
    "Curricular units 1st sem (approved)": 1.0,
    "Curricular units 1st sem (grade)": 10.2,
    "Debtor": 1,
    "Tuition fees up to date": 0
  },
  "modified": {
    "Curricular units 1st sem (enrolled)": 6.0,
    "Curricular units 1st sem (approved)": 4.0,
    "Curricular units 1st sem (grade)": 13.5,
    "Debtor": 0,
    "Tuition fees up to date": 1
  },
  "threshold": 0.38
}
```
- **Response (200 OK):**
```json
{
  "status": "success",
  "baseline": { ... },
  "simulated": { ... },
  "delta_risk_pp": -34.81,
  "direction": "reduced",
  "changed_features": [ ... ],
  "recourse_recommendation": {
    "status": "Recourse Identified",
    "current_risk": 0.642,
    "projected_risk": 0.294,
    "risk_reduction_pp": 34.8,
    "actionable_steps": [
      "Resolve tuition balance via payment plan or emergency aid referral",
      "Tutoring & exam prep to pass at least 4 curricular units"
    ],
    "feasibility": "Realistic"
  },
  "warnings": [],
  "governance_note": "Simulation displays statistical associations from historical cohort patterns only."
}
```

---

## 3. Explainability Endpoints

### 3.1 Permutation SHAP Attributions
- **URL:** `/api/explain/shap`
- **Method:** `POST`
- **Request Body:**
```json
{
  "student": { ... },
  "top_n": 12,
  "max_background": 25
}
```
- **Response (200 OK):**
```json
{
  "status": "success",
  "top_features": [
    {
      "feature": "Curricular units 1st sem (approved)",
      "shap_effect": 0.2415,
      "student_value": 1.0,
      "direction": "risk_driver",
      "interpretation": "Increases dropout probability by 0.242"
    }
  ],
  "base_prediction": 0.642,
  "additivity_error": 0.0,
  "plotly_json": { ... }
}
```

### 3.2 LIME Surrogate Rules
- **URL:** `/api/explain/lime`
- **Method:** `POST`
- **Request Body:**
```json
{
  "student": { ... },
  "top_n": 10
}
```

---

## 4. Analytics & Decision Support Endpoints

### 4.1 Dynamic Screening Threshold Evaluation
- **URL:** `/api/analytics/threshold`
- **Method:** `POST`
- **Request Body:**
```json
{
  "threshold": 0.38
}
```
- **Response (200 OK):**
```json
{
  "status": "success",
  "threshold": 0.38,
  "test_samples": 885,
  "metrics": {
    "precision": 0.7415,
    "recall": 0.7676,
    "sensitivity": 0.7676,
    "specificity": 0.8735,
    "f1_score": 0.7543,
    "accuracy": 0.8395,
    "flagged_count": 294,
    "flagged_percentage": 33.2
  },
  "confusion_matrix": {
    "tp": 218,
    "fp": 76,
    "fn": 66,
    "tn": 525,
    "display": [[218, 66], [76, 525]]
  }
}
```

### 4.2 Cohort Risk Heatmap
- **URL:** `/api/analytics/heatmap?dimension=academics`
- **Method:** `GET`
- **Dimensions Supported:** `academics`, `financial`, `scholarship`

### 4.3 Institutional Caseload & ROI Planner
- **URL:** `/api/analytics/capacity`
- **Method:** `POST`
- **Request Body:**
```json
{
  "total_students": 1200,
  "advisor_count": 4,
  "max_caseload": 60,
  "avg_tuition": 5000.0
}
```

---

## 5. Case Store & Advisor CRM Endpoints

### 5.1 Advisor Authentication
- **URL:** `/api/cases/login`
- **Method:** `POST`
- **Request Body:**
```json
{
  "username": "admin",
  "password": "Admin12345678!"
}
```

### 5.2 Case Listing & Mutation
- `GET /api/cases`: Retrieve cases for active session.
- `POST /api/cases`: Create or update a case (`{"reference": "DEMO-130", "owner": "advisor1", "status": "Needs assessment", "supports": [...]}`).
- `DELETE /api/cases/<reference>`: Delete a fictional case.
- `GET /api/cases/audit`: Retrieve immutable audit history (Admin only).

---

## 6. Formal Report Export Endpoints

### 6.1 Download PDF Dossier
- **URL:** `/api/reports/pdf`
- **Method:** `POST`
- **Response:** Binary PDF stream (`Content-Type: application/pdf`).

### 6.2 Export Markdown Dossier
- **URL:** `/api/reports/markdown`
- **Method:** `POST`
- **Response:** Formatted Markdown document.

---

## 7. MLOps Health & Drift Endpoints

### 7.1 System Health & Benchmark
- **URL:** `/api/health`
- **Method:** `GET`
- **Response:** Status of model artifact, SHA-256 signatures, pipeline, latency, and database.

### 7.2 Covariate Drift Audit
- **URL:** `/api/health/drift`
- **Method:** `GET`
- **Response:** Two-sample KS statistics and PSI distributions across all 30 monitored features.
