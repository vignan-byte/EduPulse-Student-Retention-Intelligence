# Faculty Demo Release — V4 Enhanced

Release date: 11 November 2026. Scope: academic research prototype for Group 12, INT395 Supervised Learning.

## Verified outcomes

- Dataset: UCI 697 (4,424 public records), source supplied in `data/students.csv`.
- Seven classifiers benchmarked in V3; Random Forest selected by 5-fold CV mean macro-F1 0.6819.
- V4 held-out multiclass macro-F1 0.652.
- Training-OOF-selected threshold ~0.345, holdout recall 74.3%, precision 71.3%; false negatives 73 and false positives 85.
- Automated regression suite: **11 passed**.
- Streamlit basic app smoke test using V4 model artifacts: **0 exceptions**.
- SHAP model-agnostic permutation explainer: executed on fitted Random Forest and actual UCI record, produced feature contributions.
- LIME encoded-feature explainer: executed on fitted Random Forest and actual UCI record, produced local surrogate weights.
- PowerPoint generator: completed, 10 slides.

## Functional release contents

- Professionalized Streamlit presentation with five analytic areas plus fictional-case support review.
- One-row CSV parser size bound, identity-column checks and required-feature validation.
- Three prediction stages; held-out evaluation, screening threshold trade-offs and exploratory subgroup slices.
- What-if model sensitivity on available first-semester academic features.
- SHAP/LIME and global permutation importance.
- Documentation: README, model card, presentation guide, final demo checklist and previous experimental validation reports.

## What this release DOES NOT prove

The project is not 10/10 production-ready and has not been deployed to an institution. There is no validated privacy compliance, role-based authentication, real student case store, external/temporal dataset test, formal probability calibration, prospectively measured retention improvement, or ongoing monitoring. Class imbalance and unresolved Enrolled outcomes remain limitations. The latest UI additions are smoke-tested, not comprehensively end-to-end tested across browsers.

## Resume honesty

Safe: "Built and demonstrated an explainable student-outcome ML prototype; benchmarked seven models on 4,424 public records; tested review-threshold trade-offs and interactive SHAP/LIME explanations."

Not supported: "Achieved 95% accuracy," "prevented dropouts," "used live university records," "fully secure enterprise deployment," or "10/10 industry-certified solution."
