# V5 — Calibrated Model Validation

Date: 11 November 2026. Scope: local academic research prototype, not university production.

## Changes

- Training-only sigmoid probability calibration using `CalibratedClassifierCV` (3-fold).
- Training-only cross-validated screening threshold applied to calibrated model.
- Comparisons of original versus calibrated Brier score.
- Readable raw-feature LIME explanations compatible with calibrated models.
- Dataset-label/feature validation and reproducibility metadata.
- More tests for dataset validation; model card and slides updated.

## Measured UCI 697 performance

- 4,424 student records, 885 in held-out evaluation.
- Winner from seven-model uncalibrated CV comparison: Random Forest (CV macro-F1 ~0.6819).
- Uncalibrated held-out multiclass macro-F1: ~0.652.
- Calibrated held-out multiclass macro-F1: ~0.625 (worse).
- Dropout Brier score: 0.12162 uncalibrated -> 0.11746 calibrated (better).
- Training-selected threshold: ~0.3637. Holdout: TP 211, FN 73, FP 85, TN 516; dropout precision ~71.3%, recall ~74.3%.
- SHAP and LIME ran successfully on one calibrated Random Forest prediction using a real UCI record.

## Interpretation

Probability quality improved on the held-out data according to the Brier score, while three-class classification macro-F1 fell. This is a real trade-off. Internal calibration does **not** establish reliability on another college or later cohort. The threshold is a research example only.

## Remaining for actual industry deployment

External/temporal validation, stakeholder-defined operating policies, more extensive explanation testing, real identity/access controls, audited data retention/deletion, secure hosting, CI/CD monitoring, independent fairness assessment, human-subject approval where required, and measured intervention outcomes.
