# Interview and demonstration

## Resume description

Developed a Streamlit student-retention research platform using seven supervised classifiers, leakage-conscious preprocessing, calibrated dropout probabilities, SHAP/LIME explanations and a role-controlled SQLite workflow for fictional advisor cases and follow-ups. Evaluated on a stratified public-data holdout and documented fairness, privacy and external-validation limitations.

## Demonstration checklist

1. Install, train, test and launch using README commands.
2. Show model comparison, confusion matrix, calibration and subgroup errors.
3. Preview a public UCI row and explain the probability uncertainty.
4. Show evidence-triggered support suggestions; avoid causal claims.
5. Execute SHAP and LIME; explain why they may disagree.
6. Upload a feature-only public batch and filter advisor review priorities.
7. Create admin/advisor accounts; sign in and save a fictional case.
8. Record contact outcome and follow-up date. Sign in as another advisor to demonstrate ownership isolation.
9. Delete the case; show minimal admin audit.
10. Explain that contact outcomes do not measure intervention efficacy.

## Questions and answers

**Why macro-F1?** It weights each class equally and exposes weak Enrolled classification despite higher overall accuracy.

**How is leakage reduced?** Stage-specific known features and preprocessing inside CV pipelines. Timestamp uncertainty still prevents a claim of complete temporal safety.

**Why calibration?** It improves interpretability of probability estimates. Compare actual Brier scores instead of assuming benefit.

**Where is the threshold chosen?** Out-of-fold training predictions, independently of test labels. Model-family selection precedes OOF prediction, so the process is not fully nested model-selection validation.

**Does SHAP explain causes?** No. It attributes model predictions relative to a selected background distribution. Correlated predictors can redistribute contributions.

**Why LIME disagreement?** Local perturbations and surrogate approximation differ from SHAP's attribution procedure. Neither guarantees stable explanations for all records.

**What proves retention improvement?** Nothing in this release. A governed prospective evaluation with outcomes and a suitable comparison design is needed.

**Is this production-ready?** No. It is a measured local portfolio demonstration with fictional case management, requiring institutional external validation and substantial IAM/privacy work before real use.
