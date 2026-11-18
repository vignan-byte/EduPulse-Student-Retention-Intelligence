# V6 — Engineering Upgrade

Release candidate: 11 November 2026. Based on V5 calibrated academic research prototype.

## Added

1. SHA-256 local artifact manifest and integrity check before model loading.
2. Model/metrics stage and class consistency checks.
3. Offline numeric and categorical feature-distribution shift reporting.
4. GitHub Actions CI workflow for Python setup, compilation and pytest.
5. Regression tests for corrupted artifact detection and drift calculations.

## Safety boundaries

SHA-256 manifest is not a digital signature or authentication mechanism. It detects accidental changes but cannot prove publisher identity. Joblib uses pickle and must never be loaded from an untrusted source. Drift checks are exploratory and do not replace real-time monitoring, privacy controls or data-governance review.

## Outstanding production work

Authentication, authorization, secure database, real audit log, external/temporal validation, calibrated probability acceptance policy, deployed monitoring, rollback, prospective evaluation of interventions and institutional governance are still absent.
