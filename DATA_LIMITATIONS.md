# Data Provenance, Limitations & Ethical Boundaries

**Student Retention Intelligence (INT395 Group 12)**  
*A Transparent Audit of Data Boundaries and Pre-Production Constraints.*

---

## 1. Data Provenance & Institutional Context

- **Source Dataset:** Published [UCI Machine Learning Repository Dataset #697](https://archive.ics.uci.edu/dataset/697/predict+students+dropout+and+academic+success) (*"Predict Students' Dropout and Academic Success"*).
- **Institution of Origin:** Higher education institution in Portugal (Polytechnic Institute of Portalegre).
- **Cohort Span:** Undergraduate cohorts across 17 distinct degree programs (Agronomy, Design, Education, Nursing, Management, Social Service, Technologies).
- **Dataset Size:** 4,424 historical records across 36 predictors.

---

## 2. Key Data Limitations

### A. Lack of Per-Event Timestamp Provenance
While the dataset cleanly records first-semester curricular units (`credited`, `enrolled`, `evaluations`, `approved`, `grade`), it **lacks exact granular calendar timestamps** for individual transaction events. 
- *Institutional Impact:* We cannot ascertain whether a fee payment delay occurred in week 2 or week 14. 
- *Deployment Prerequisite:* Before deploying in a live university Student Information System (SIS), data pipelines must ingest immutable, point-in-time timestamped snapshots to guarantee zero forward temporal leakage.

### B. Absence of Attendance and LMS Engagement Metrics
The UCI dataset does not include individual lecture attendance logs, LMS (Canvas/Moodle/Blackboard) clickstreams, or assignment submission latency.
- *Clinical Impact:* Models rely heavily on end-of-semester approved units and grades. In a modern institutional LMS, daily engagement drops can provide warning signals weeks before final exams.
- *Academic Honesty:* We deliberately do not fabricate synthetic attendance columns; the model utilizes only genuine verified predictors.

### C. The Intermediate 'Enrolled' Status
In the 3-class target distribution, 18.0% (794 students) are classified as `Enrolled`.
- These are active students who have neither graduated nor dropped out within the measured time horizon.
- Treating `Enrolled` as a binary negative (i.e. "retained") is statistically flawed because a significant fraction may discontinue in subsequent semesters. Preserving multiclass probability distributions prevents over-optimistic graduation claims.

### D. Institutional Transferability Boundaries
Higher education dynamics vary widely across institutions, regions, and curriculum structures:
- A model trained on a European polytechnic institute cannot be assumed to generalize directly to an American research university or an Indian engineering college without **local domain adaptation and recalibration**.
- To demonstrate how to evaluate transferability, this repository includes an offline evaluation CLI (`src/external_eval.py`) and covariate drift monitor (`src/monitor.py`).

---

## 3. Privacy, Security & PII Protection

1. **Synthetic & Anonymized Demonstration Data:**
   - All demonstrations and preloaded profiles use strictly fictional references (`DEMO-001`, `DEMO-101`).
   - No living student identities, emails, or personal identifiers are stored or processed.

2. **Automated Input Guardrails:**
   - Any uploaded CSV is screened by `src/safety.py` using regex pattern matching for identifying keys (`name`, `email`, `phone`, `student_id`, `aadhaar`, `roll_no`).
   - Upload payloads are strictly constrained to 250 KB and 500 rows maximum to prevent memory exhaustion attacks.

3. **Cryptographic Integrity:**
   - Saved model bundles (`model.joblib`) are verified against SHA-256 manifests (`manifest.json`) prior to deserialization to prevent arbitrary pickle payload execution.
   - User credentials in the local demonstration CRM are salted with 16 random bytes and hashed using PBKDF2-SHA256 with 310,000 rounds.

---

## 4. Ethical Charter & Non-Punitive Mandate

> **Core Principle:** Machine learning predictions describe historical statistical correlations—they do **NOT** determine a student's capability or future destiny.

1. **Voluntary Support Only:** Predictions must solely trigger voluntary, supportive outreach (e.g. tutoring invitations, financial aid advising, wellness check-ins).
2. **Prohibition of Punitive Actions:** Using model predictions to deny admission, revoke scholarships, enforce academic probation, or disqualify students is **strictly prohibited**.
3. **Right to Human Explanation:** Every flagged student has the right to understand the factors influencing an advisor's outreach, supported by the platform's SHAP and LIME visual explainers.
