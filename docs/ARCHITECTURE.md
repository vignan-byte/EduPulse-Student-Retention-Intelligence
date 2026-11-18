# Architecture

```mermaid
flowchart TD
  A[Public UCI data] --> B[Stage and schema checks]
  B --> C[Stratified training split]
  C --> D[Pipeline CV and tuning]
  D --> E[Calibration and OOF threshold]
  E --> F[Trusted local model bundle]
  F --> G[Streamlit analysis]
  G --> H[SHAP and LIME]
  G --> I[Human advisor review]
  I --> J[SQLite fictional cases and follow-ups]
  F --> K[Held-out evaluation and drift CLI]
```

src/ml.py owns model experiments. src/intelligence.py owns support rules and cohort inference. src/safety.py bounds uploads. src/explain.py owns explanations. src/case_store.py enforces local advisor ownership using the authenticated Streamlit actor. Its Python methods assume a trusted caller; they are not remotely exposed APIs. src/registry.py verifies local model hashes before loading trusted joblib files. A malicious model publisher can replace both hashes and executable pickle content.

Uploads remain in session memory. SQLite contains fictional case references, structured support/contact outcomes and user password hashes. Audit is local and mutable by the OS/database administrator, not tamper-proof. Case identity is intentionally not automatically linked to historical UCI rows.
