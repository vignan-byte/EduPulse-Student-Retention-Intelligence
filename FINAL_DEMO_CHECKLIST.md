# Tomorrow's Demo Readiness Checklist

## Before presenting

- [ ] Use the extracted V4 Faculty Demo edition, not an older flattened ZIP.
- [ ] Open the correct project folder in VS Code (contains `app.py`, `src/`, `tests/`).
- [ ] Install requirements into its own `.venv` with the direct venv Python path.
- [ ] Run `python -m src.train --full-benchmark` using the venv interpreter (V5 calibration enabled). Dataset is bundled for offline use.
- [ ] Run `python -m pytest -q` with the venv interpreter.
- [ ] Launch `python -m streamlit run app.py` using the venv interpreter.
- [ ] Test Overview, Model Evaluation, Student Assessment, Explainability and Support Review tabs.
- [ ] Use anonymized public UCI records, never classmates' actual information.
- [ ] Keep the PowerPoint, model card and validation report ready locally.

## Suggested demo sample

1. Overview: show 4,424 historical records and class distribution.
2. Model Evaluation: explain seven-model CV, held-out macro-F1 and screening trade-off.
3. Student Assessment: tick the built-in UCI sample, choose row 130, inspect probabilities.
4. What-if: adjust a semester-1 academic input and describe model sensitivity only.
5. Explainability: use LIME first (usually faster), then SHAP if time permits.
6. Support Review: use DEMO-001 and predefined voluntary support choices.

## Emergency fallback

- If SHAP is slow, show LIME and explain that SHAP has been independently smoke-tested.
- If the browser page is blank, inspect terminal tracebacks; don't modify model artifacts manually.
- If Python imports fail, verify `src/train.py`, `src/ml.py` exist and launch from the project root.
- If there is no internet, omit `--download` because the dataset is included.

## Honesty statement

This is a professional-looking and reproducible **academic research prototype**. It is *not* a production-ready system for acting on real student records; credentials, governance, external validation and monitoring are missing. Use the phrase "local interactive demonstration" rather than "deployed to a university".
