# V7 — Local Advisor Security Demonstration

Changes over V6:

- Added salted PBKDF2-HMAC-SHA256 password storage for local demo accounts.
- Added administrator and advisor roles, owner-scoped fictional case access, and denial of cross-advisor updates.
- Added SQLite persistence for `DEMO-` reference cases with predefined support choices, plus audit events and controlled deletion.
- Added CLI for creating users without hardcoded passwords.
- Added Streamlit sign-in and admin/advisor demonstration workflows.
- Added regression tests for authentication, ownership, role checks, rejection of real references, audit visibility and deletion.

**Limitations:** This is a localhost research workflow using fictional identifiers. No MFA, external IdP, hardened sessions, verified hosted TLS, full encryption/security review, independent institutional validation or lawful real-student data processing. Internal Python service methods rely on a trusted caller to supply a verified actor identity; the demonstration cannot be treated as a production authorization service.
