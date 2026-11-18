# Render deployment readiness

This is a review branch, not a verified production release.

- The production app requires a strong EDUPULSE_SECRET_KEY and EDUPULSE_ADMIN_PASSWORD, both configured as Render secrets.
- Public deployment must not include the tracked local_demo database or any seeded demo credentials.
- Production sessions use HTTPS-only cookies.
- CRM bootstrap is disabled unless explicitly enabled and provided with an administrator password.
- SQLite on Render free is ephemeral: CRM writes will not persist across restarts or deploys. Do not use it for real student data.
- Required before merge: test model loading on the selected Python and scikit-learn versions; run automated and browser tests; review CSRF protection, login throttling, XSS in CRM tables, and committed demonstration database contents.
- Do not create paid services without user approval.
- Deploy using the Blueprint in render.yaml only after review and merge.
