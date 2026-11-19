# EduPulse Flask v11 — Render deployment review

**Live Production URL:** [https://edupulse-flask-th4m.onrender.com](https://edupulse-flask-th4m.onrender.com)
**Live Healthcheck:** [https://edupulse-flask-th4m.onrender.com/api/health](https://edupulse-flask-th4m.onrender.com/api/health)
**Live Liveness Probe:** [https://edupulse-flask-th4m.onrender.com/api/health/live](https://edupulse-flask-th4m.onrender.com/api/health/live)

## Implemented on this PR branch
- Strong production secret validation and HTTPS-only session cookies.
- New production SQLite database path, separate from the former committed demo DB.
- Admin account bootstrapped only with an operator-provided environment password.
- Removed the committed demo SQLite database from the current branch and removed displayed demo credentials from login pages. **The old database and passwords still exist in public Git history**. Removing a file does not erase historical commits. Do not reuse those passwords.
- Added CSRF token checks for advisor CRM mutations, token-aware browser calls, basic per-process login throttling, HTML escaping for CRM table data, and response security headers.
- Pinned scikit-learn to 1.7.2, the version embedded in the saved model estimators; added artifact compatibility regression tests.
- Added a GitHub Actions pull-request workflow and a free-plan Render Blueprint.

## Checks and known limitations
- CI workflow must finish successfully before merging. Its existence does **not** mean the tests have passed.
- In this assistant environment, the artifact SHA-256 checks passed using the matching uploaded source archive. The model deserialized under scikit-learn 1.8.0 with version warnings; that is not equivalent to successful inference under the pinned 1.7.2 deployment environment.
- The rate limiter is in-memory and per-process, not a distributed defense. For a higher-risk public service use a shared limiter and stronger authentication controls.
- Existing inline JavaScript and external CDNs prevent introducing a strict Content-Security-Policy without further refactoring.
- The default production SQLite path /tmp/edupulse/cases.sqlite3 is **ephemeral** on Render free; cases and users may disappear on restart/redeploy. Do not store real student records.
- Local CRM account creation is now an explicit setup step. Previously embedded demo credentials are no longer automatically created.
- The README's claimed evaluation metrics may differ from the committed metrics.json; reconcile before academic/public claims.

## Deployment gate
1. Inspect GitHub Actions results for this PR; correct any failures.
2. Manually smoke-test all 11 pages, ML prediction, SHAP/LIME, PDF export, CRM authentication and mutations, and security responses.
3. Confirm no private student data or credentials are present in current files or public Git history. Consider rotating credentials and sanitizing history if needed.
4. Merge this PR into main after review.
5. In Render, create a Blueprint from render.yaml on main, **confirm the free plan** and provide EDUPULSE_ADMIN_PASSWORD securely. The Blueprint generates EDUPULSE_SECRET_KEY.
6. Verify /api/health and the public site after deployment. Do not create paid resources without approval.
