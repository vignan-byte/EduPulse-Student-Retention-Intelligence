# Group 12 — Faculty Demo and Viva Guide

## Opening statement (30 seconds)

"Our project is an early student-outcome and dropout-risk research prototype. It uses supervised learning on a public higher-education dataset, compares multiple algorithms, explains individual predictions, and demonstrates how an advisor could review potential support needs. We deliberately avoid treating a prediction as a decision about a student's future."

## Suggested live demo (6–8 minutes)

1. **Overview:** Show the original UCI class distribution and model scores. Clarify historical outcomes.
2. **Model Evaluation:** Show CV results for all seven algorithms, the held-out confusion matrix, and the precision/recall trade-off. Highlight why macro-F1 alone is insufficient.
3. **Student Assessment:** Choose a historical UCI record, show the three outcome probabilities and the research threshold. Demonstrate a what-if grade or approved-subject change, saying it is model sensitivity—not a causal intervention experiment.
4. **Explainability:** Run LIME and SHAP on a selected record. Emphasize that explanations describe model prediction behavior.
5. **Support Review:** Add fictional `DEMO-001` with tutoring and academic advising, then export the in-session CSV. Explicitly state that real student records are not stored.
6. **Methodology:** Explain data leakage prevention at admission/semester stages and the validation protocol.

## Key numbers (actual tested benchmark)

- Dataset: UCI 697; 4,424 historical student records; classes Dropout, Enrolled, Graduate.
- Seven-algorithm cross-validation benchmark winner: Random Forest.
- Five-fold training CV macro-F1: 0.6819 (SD 0.0217).
- Held-out multiclass macro-F1: approximately 0.625 with V5 sigmoid calibration (versus 0.652 without calibration).
- Default dropout threshold 0.50: 169 TP, 115 FN, 28 FP, 573 TN.
- V5 training-selected threshold approximately 0.364: 211 TP, 73 FN, 85 FP, 516 TN.
- At selected threshold, dropout recall ~74.3%, precision ~71.3% on held-out data.
- Dropout Brier score: ~0.1216 baseline, ~0.1175 after calibration. Better calibration came with a drop in multiclass macro-F1.

## Questions faculty may ask

**Why classification, not regression?** The output has three categorical outcome classes.

**Why Random Forest?** It had the highest cross-validated macro-F1 among the seven models in our benchmark. The margin over Logistic Regression and SVM is small and does not prove universal superiority.

**What is data leakage?** Training on information unavailable at prediction time, or fitting preprocessing to test data. We isolate preprocessing inside training pipelines and omit future-semester fields for earlier prediction stages.

**Why isn't accuracy enough?** The classes are imbalanced. Macro-F1 and confusion matrices reveal performance differences between labels.

**What's the difference between SHAP and LIME?** SHAP attributes a prediction across features relative to a background distribution; LIME fits an approximate local surrogate around one example. Both describe model behavior, not causes.

**What about false negatives?** At a support-review threshold, false negatives mean dropout-labeled records were not flagged. Improving recall can increase false positives; both have real operational costs.

**Is the system ready for college deployment?** No. It needs permissioned institutional data, external/temporal validation, calibration, privacy controls, educator review and ongoing monitoring.

**Why not include attendance?** The public UCI dataset used here does not provide individual attendance percentages. We do not invent them.

## Responsible resume description

**Student Retention Intelligence | Python, Scikit-learn, Streamlit, SHAP, LIME** — Developed a reproducible student-outcome classification prototype using 4,424 public records; benchmarked seven algorithms with five-fold CV; implemented training-only review threshold selection, error analysis, explanation tools, and an interactive demonstration dashboard. Achieved ~0.652 held-out macro-F1; measured ~74.3% dropout recall at a training-selected screening threshold (71.3% precision). Research prototype, not deployed to an institution.
