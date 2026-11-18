# Faculty Demonstration & Viva Defense Guide

**Project:** Student Retention Intelligence System (EduPulse)  
**Course:** INT395 — Supervised Learning (Group 12)  
**Academic Year:** 2026–2027  
**Team Members:** Kabya Varun • Duggisetty Vasavi Vignan • Shivraj Singh  

---

## 1. Quick Launch Commands (Windows PowerShell)

Open PowerShell in the project directory:

```powershell
# 1. (Optional) Run automated tests to verify system health (42 tests)
python -m pytest -q

# 2. Run the headless integration smoke test
python -m scripts.smoke_app

# 3. Launch the professional application
python -m streamlit run app.py
```

The application opens at **`http://localhost:8501`**.

---

## 2. Recommended Live Demonstration Flows

### Flow A: The 5-Minute Executive Walkthrough (Fast Viva Defense)

| Time | Page / Feature | Action & Script |
|---|---|---|
| **0:00 – 1:00** | **🎓 Faculty Demo Mode** (Stage 1 & 2) | Click **"Faculty Demo Mode"** in the sidebar. Introduce the problem: First-year higher education attrition using 4,424 records from published UCI 697. Highlight the 3-class target (`Dropout`, `Enrolled`, `Graduate`) and strict stage-based data leakage prevention. |
| **1:00 – 2:00** | **🎓 Faculty Demo Mode** (Stage 3 & 4) | Advance to **Stage 3** (Benchmark): Show the 8-model comparison table. Explain why **Macro-F1 (0.684)** was the selection metric instead of accuracy. Advance to **Stage 4**: Select *"High Risk Profile"*, click **"Run Live AI Prediction"**, and show the real-time probability breakdown (Dropout ~68.4%, Enrolled ~16.2%, Graduate ~15.4%). |
| **2:00 – 3:30** | **🎓 Faculty Demo Mode** (Stage 5 & 6) | Advance to **Stage 5** (Explainability): Click **"Compute Real SHAP Attribution"** to show the mathematical contribution of credits and debtor status. Advance to **Stage 6** (What-If): Show the **Before-and-After Sensitivity Card**; increase approved units from 1 to 5 and show the risk drop from ~68% down to ~18% (-50 pp). |
| **3:30 – 4:30** | **🎓 Faculty Demo Mode** (Stage 7 & 8) | Advance to **Stage 7** (Support): Point out the rule-based tutoring and financial aid referrals. Advance to **Stage 8** (Error Analysis): Explain the operational cost of False Positives (79) vs False Negatives (57), and show why sigmoid probability calibration lowered Brier score from 0.119 to 0.106. |
| **4:30 – 5:00** | **Conclusion & Questions** | Conclude on **Stage 9** (Architecture): Highlight PBKDF2 password security, local SQLite CRM, non-punitive ethical mandate, and answer faculty questions. |

---

### Flow B: The 10-Minute Deep-Dive Demonstration

1. **Overview Dashboard (2 mins):**
   - Click **📊 Overview**.
   - Review the 6 executive KPI cards (4,424 students, 31.6% flagged, 74.2% holdout accuracy, 79.9% recall, 74.2% precision, 0.106 Brier score).
   - Walk through the **4 Key Retention Insights** (e.g. 50% credit threshold, debtor sensitivity, enrolled complexity).
2. **Student Risk Intelligence & Sensitivity Lab (2 mins):**
   - Click **🎯 Student Risk Intelligence**.
   - Switch between preloaded personas (*High Risk*, *Moderate Risk*, *Dean's List Scholar*).
   - Click **📝 Student Assessment**: Use the **Before-and-After Sensitivity Card** to demonstrate real-time what-if shifts.
   - Show the **Actionable Counterfactual Recourse** targets.
   - Click **Download Printable Retention Dossier (.md)** to show the generated student report.
3. **Model Performance Lab (2 mins):**
   - Click **🔬 Model Performance**.
   - Show the 8-algorithm benchmark table (highlighting Stacking Ensemble and Logistic Regression).
   - Show the Multiclass OvR ROC curves (Macro AUC = 0.855) and Precision-Recall curves.
   - Show the **Reliability Diagram** and the **Operational FP vs FN Trade-off Card**.
   - Move the **Threshold Simulator** slider to show dynamic recalculation of metrics.
4. **Explainable AI Center (1.5 mins):**
   - Click **🧠 Explainable AI**.
   - Compute Permutation Feature Importance.
   - Generate Local SHAP & LIME charts for record 130. Explain the distinction between associative attribution and causal claims.
5. **Intervention Planning CRM (1.5 mins):**
   - Click **🤝 Intervention Planning**.
   - Sign in with `advisor1` / `AdvisorPass12345!`.
   - Log a fictional case (`DEMO-101`), select voluntary support options, schedule a follow-up, and show the audit trail.
6. **Institutional Analytics (1 min):**
   - Click **📈 Institutional Analytics**.
   - Adjust cohort size (1,200) and available advisors (4) to show the capacity recommendation and modeled tuition preservation.

---

## 3. Preloaded Fictional Demonstration Personas

| Profile Name | Academic Standing | Financial / Demographic Status | Expected Model Prediction |
|---|---|---|---|
| **🔴 High Risk** | 1 of 6 units approved (16.7%), GPA: 10.2/20 | Debtor: Yes, Tuition: Past due, Age: 22 | **Dropout (~68–75%)** <br>*Status: CRITICAL / ADVISOR REVIEW* |
| **🟡 Moderate Risk** | 3 of 6 units approved (50.0%), GPA: 11.4/20 | Debtor: No, Tuition: Current, Age: 19 | **Enrolled / Moderate (~32–42%)** <br>*Status: MODERATE MONITORING* |
| **🟢 Low Risk (Scholar)** | 6 of 6 units approved (100%), GPA: 15.6/20 | Debtor: No, Tuition: Current, Scholarship: Yes | **Graduate (>85%)** <br>*Status: ON TRACK / ROUTINE* |

---

## 4. Expected Faculty Questions & Model Answers

### Q1: Why did you choose classification instead of regression?
> **Answer:** "Student retention in this institutional setting has three distinct categorical terminal states: *Dropout*, *Enrolled*, and *Graduate*. An unresolved *Enrolled* student cannot be treated as a numerical midpoint on a continuous scale between dropout and graduation. Classification with multi-class calibrated probabilities allows us to capture the probabilistic uncertainty across all three states."

### Q2: Why is Macro-F1 your primary model selection metric instead of Accuracy?
> **Answer:** "The dataset exhibits class imbalance (49.9% Graduate, 32.1% Dropout, 18.0% Enrolled). A naive model predicting only the majority classes could score over 72% accuracy while completely failing to identify vulnerable students. Macro-F1 gives equal weight to all three classes, exposing the true diagnostic performance on the difficult-to-classify intermediate students."

### Q3: How did you prevent data leakage?
> **Answer:** "We implemented strict stage-specific feature allowlists in `src/ml.py`. At the 'After Semester 1' checkpoint, all second-semester predictors are stripped out before modeling. Furthermore, all preprocessing—including categorical one-hot encoding, numeric median imputation, and standard scaling—is encapsulated inside scikit-learn pipelines fitted strictly on training folds during cross-validation, with zero test-set contamination."

### Q4: Does SHAP prove that poor grades *cause* dropout?
> **Answer:** "No. SHAP computes mathematical Shapley values describing how much a feature shifted the model's logit prediction relative to an expected background distribution. It identifies statistical associations in historical data, not causal mechanisms. We explicitly instruct advisors that SHAP provides diagnostic clues, not deterministic or causal destiny."

### Q5: What is the operational cost of False Positives vs. False Negatives?
> **Answer:** "A False Positive means an advisor invites a student to a voluntary check-in who would have graduated on their own (costing 30 minutes of staff time). A False Negative means an at-risk student drops out without being offered support (costing the student their degree and the university years of tuition). That is why we tuned our operational threshold to 37.7%, prioritizing recall (79.9%) over precision (74.2%)."

---

## 5. Emergency Fallback & Troubleshooting

- **If an explanation takes too long:** Switch to LIME (instant surrogate) or use pre-computed samples in the Overview and Evaluation tabs.
- **If credentials are forgotten:** Use `admin` / `AdminPass12345!` or `advisor1` / `AdvisorPass12345!`.
- **Offline Reliability:** Public source dataset is bundled locally in `data/students.csv`. No internet connection is needed for live demonstration.
