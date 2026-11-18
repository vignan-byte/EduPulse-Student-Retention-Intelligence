# V8 Final Release Candidate — Honest Quality Gate

Project: Student Dropout Risk & Retention Intelligence System (INT395, Group 12).

## New in V8

- Independent labeled-cohort evaluation CLI with bootstrap 95% macro-F1 interval.
- Better subgroup diagnostics: minimum positive/negative counts, precision, recall, and false-positive rate.
- Dockerfile with non-root runtime, health check, and public-dataset training at build time.
- GitHub Actions workflow expanded to train a model and run Streamlit smoke checks after unit tests.
- Dedicated reusable app integration smoke script.

## Verified versus unverified

- Local unit and integration checks: see final release terminal results.
- Verified existing UCI benchmark measurements remain the best reproducible internal evidence.
- No external institutional dataset has been provided, therefore **external validation is not completed**.
- Docker executable was unavailable in this environment, therefore image build and runtime were **not verified**.
- GitHub workflow is included but has not been run on GitHub from this environment.
- No actual institution has approved or adopted the system.

## Final engineering verdict

This is a strong, reproducible, carefully scoped academic research prototype. It is not a certified or 10/10 production-grade system. Outstanding external dependencies include institution authorization/data, legal/privacy review, validation on independent cohorts, meaningful pilot outcomes, and hardened production identity/operations.
