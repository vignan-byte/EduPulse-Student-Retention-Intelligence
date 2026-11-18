# Final engineering audit — 11 November 2026

## Evidence and scope

V8 baseline: 27 tests passed before changes. Final suite: 37 passed in 4.13 seconds (one dependency deprecation warning). See evidence/evidence_tests.txt. Training executed on the included public dataset, seed 42: 3,539 training records and 885 held-out records. Seven algorithms completed five-fold stratified CV. The selected family is logistic; randomized search retained all trial scores in evidence/metrics.json. No V8-model improvement claim is supported because a paired V8 experiment was not run.

## Measured performance

| Metric | Final held-out result |
|---|---:|
| Accuracy | 0.7424 |
| Macro-F1 | 0.6074 |
| Balanced accuracy | 0.6186 |
| Macro OVR ROC-AUC | 0.8555 |
| Dropout Brier | 0.1063 |
| Review threshold (training OOF) | 0.3772 |
| Dropout precision at review threshold | 0.7418 |
| Dropout recall at review threshold | 0.7993 |
| False positives / false negatives | 79 / 57 |

Per-class precision, recall, F1, confusion matrix, subgroup slices, calibration error and calibration comparison are in evidence/metrics.json. The threshold's 75% training precision target did not hold on test (74.18%); it is an experimental operating point. Weak Enrolled classification remains a material limitation. Algorithm comparison uses multiple reported metrics, with macro-F1 as the explicit selection rule; there is no composite arbitrary score.

## Changes and checks

Strict known-column stage filtering rejects unknown outcome proxies. Numeric upload checks reject extra columns, infinities and invalid cells; batch bounds are 500 rows / 250 KB. Evidence-triggered support recommendations replace the unconditional generic suggestion. Follow-up dates and structured contact outcomes use advisor ownership checks and cascade deletion. Global SHAP estimates mean absolute contributions on a small sample; local SHAP reconstructs the model output within tolerance. Local LIME also executed. Execution logs and explanation outputs are included.

Corrected the Marital Status categorical mismatch and reran the entire experiment. The preliminary pre-correction run selected forest with macro-F1 0.6253; this exploratory result is not the final schema-correct experiment. The final model has higher accuracy but lower macro-F1 than that preliminary run. Hyperparameter trials can fail to improve scores; all measured trials remain visible. A model-selection CV score is optimistic after choosing/tuning the winner and is not a nested-CV generalization estimate.

## Security and fairness assessment

Existing ownership, authentication, invalid-upload, artifact-integrity, drift and external-evaluation tests were preserved. Added tests cover follow-up authorization/deletion, numeric attacks, batch validation, known-field rejection, support triggers and trained-artifact inference. This audit was performed by the implementing assistant, not an independent third-party auditor. No penetration test or production privacy certification occurred.

Subgroup slices in metrics use a fixed 0.5 screening threshold, not the selected review threshold. Differences in error rates require further investigation and uncertainty estimates. Small-cell suppression does not establish fairness. Protected attributes remain in the benchmark and require policy review. No independent institutional validation or demonstrated retention benefit exists.

## Verified boundary and remaining work

Linux tests, model training, SHAP/LIME scripts and Streamlit AppTest checks executed. The live Streamlit HTTP health endpoint returned ok; see evidence/evidence_health.txt. Docker is unavailable in this environment; no Docker build, cloud deployment, Windows execution or remote GitHub Actions success is claimed. CI and Docker configurations are provided for later execution.

The dashboard is a local public-data demonstration; login restricts fictional cases only. It lacks institution-wide IAM, central throttling, session expiry and encrypted managed storage. Feature timestamp provenance remains unresolved. There are no actual attendance records, longitudinal student tracking, causal recommendations, automatic prediction-to-case linkage or intervention-effect estimates. Follow-up outcomes describe contact/support uptake only.

## Evidence-based assessment

Academic quality: strong supervised-learning demonstration with explicit reproducibility and honest evaluation limits. Portfolio quality: credible end-to-end local prototype, strengthened by measured experiments and functioning fictional advisor workflows. Production readiness: pre-production research demonstration; real student deployment is blocked by external/temporal validation, point-in-time feature provenance, enterprise access controls, privacy approval and prospective intervention evaluation. No perfect score is justified.
