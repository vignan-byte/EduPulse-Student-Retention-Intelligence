# V4 Validation Report — Student Retention Intelligence

Date: 11 November 2026. Dataset: UCI 697 (4,424 historical students). Prediction stage: end of semester 1. Model chosen by five-fold training CV: Random Forest. Holdout: 20% stratified, 885 rows. This is a local educational prototype, not an approved institutional decision system.

## Verified

- `python -m pytest -q`: **7 passed** (one third-party pytest deprecation warning).
- `python -m src.train --stage "After semester 1" --output artifacts/v4`: completed, test macro-F1 **0.652**.
- Streamlit AppTest basic execution against existing local model artifacts: **0 exceptions**. This is a smoke test, not end-to-end UI testing.
- ZIP entries preserve `src/`, `tests/`, and top-level application files.

## Holdout dropout-screening comparison

| Measure | Default 0.50 threshold | Training-OOF-selected ~0.345 threshold |
|---|---:|---:|
| True positives | 169 | 211 |
| False negatives | 115 | 73 |
| False positives | 28 | 85 |
| True negatives | 573 | 516 |
| Precision | 85.8% | 71.3% |
| Recall | 59.5% | 74.3% |

Threshold selection used out-of-fold predictions from training records, with a target of at least 75% precision in cross-validation. Actual held-out precision was lower; this illustrates why the threshold is **not ready for deployment**. It must undergo calibration, external/temporal validation, fairness review and stakeholder approval.

## Added since V3

1. Training-only threshold selection, preventing direct tuning against the final holdout.
2. Screening outputs in the dashboard with thresholds and honest warnings.
3. A local, fictional-case support review demonstration using session memory only.
4. Two new regression tests; dashboard smoke test.

## Known limitations and risks

- SHAP/LIME remain optional and were not yet validated end-to-end.
- No authentication or authorization; do not put real student records into the app.
- No durable case management or encrypted/audited student-data storage.
- No external institution validation, formal calibration model, prospective intervention trial, or causal interpretation.
- No automatic intervention should be triggered from these outputs.
- The category `Enrolled` is an unresolved student outcome, not proven lifelong non-dropout.

## Next acceptance gates

1. Model-card and risk assessment reviewed by educators and privacy stakeholders.
2. Calibrated probabilities and validation-only operating policy with external holdout.
3. SHAP/LIME numerical and visual consistency tests.
4. Role-based authorization, data minimization, retention/deletion policy and audit history if using authorized student records.
5. Full integration/e2e tests, deployment monitoring, drift detection, rollback and documented operational ownership.
