# Verified ML benchmark — 11 November 2026

Dataset: UCI 697, 4,424 historical records. Stage: after semester 1. Training uses a stratified 80/20 hold-out split and five-fold stratified CV on training data. The selected model is chosen by mean cross-validation macro-F1, then evaluated once on the holdout.

| Algorithm | CV macro-F1 mean | CV SD |
|---|---:|---:|
| Random Forest | 0.6819 | 0.0217 |
| Logistic Regression | 0.6801 | 0.0169 |
| SVM | 0.6787 | 0.0116 |
| Gradient Boosting | 0.6554 | 0.0210 |
| Decision Tree | 0.6254 | 0.0178 |
| KNN | 0.5503 | 0.0150 |
| Gaussian Naïve Bayes | 0.2136 | 0.0084 |

Selected: Random Forest. Holdout macro-F1: **0.652** (fresh seven-model benchmark run).

Dropout class screening at an illustrative 0.50 probability threshold (retrospective holdout analysis):

- True positives 169; false negatives 115; false positives 28; true negatives 573.
- Dropout precision 0.858; recall 0.595.
- Dropout Brier score 0.1216; ten-bin expected calibration error 0.0650.

**Interpretation:** A high precision with considerably lower recall indicates many truly dropout-labeled records were not flagged at this threshold. Do not select or advertise this threshold for live decisions based on the holdout. Screen thresholds on a validation set and confirm with independent data.

**Limits:** The UCI target includes an unresolved `Enrolled` category. No causal claims, institutional transferability claims, or deployment-ready fairness conclusions are justified. The subgroup diagnostics are exploratory. Probability calibration and external validation remain incomplete. These results were computed in the development environment, and minor differences may occur with package versions.

Commands: `python -m pytest -q` (5 passed); `python -m src.train --stage "After semester 1" --full-benchmark --output artifacts/full_benchmark` (completed).
