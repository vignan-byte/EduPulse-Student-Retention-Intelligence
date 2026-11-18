# Model Evaluation, Calibration & Diagnostics Report

**Project:** Student Retention Intelligence System  
**Course:** INT395 — Supervised Learning (Group 12)  
**Evaluation Dataset:** UCI 697 Held-Out Split (885 Rows, 20% Stratified Holdout)  

---

## 1. Eight-Algorithm Benchmark Comparison

Training was conducted using **5-fold stratified cross-validation** on 3,539 training records with seed 42. All preprocessing (median imputation, standard scaling, and one-hot encoding) was fitted strictly inside CV fold pipelines.

| Algorithm | CV Macro-F1 Mean | CV Macro-F1 SD | CV Accuracy | CV Balanced Accuracy | CV Log-Loss | Selection Decision |
|---|---|---|---|---|---|---|
| **Stacking Classifier (Ensemble)** | **0.6842** | **±0.0182** | **74.12%** | **68.91%** | **0.612** | **Top Candidate (Ensemble)** |
| **Logistic Regression (Balanced)** | **0.6806** | **±0.0192** | **72.31%** | **68.67%** | **0.679** | **Winner (Single Family)** |
| **Support Vector Machine (RBF)** | 0.6785 | ±0.0174 | 72.05% | 68.49% | 0.619 | Strong non-linear baseline |
| **Random Forest (Balanced)** | 0.6778 | ±0.0257 | 73.66% | 67.40% | 0.697 | Robust tree ensemble |
| **Gradient Boosting Classifier** | 0.6584 | ±0.0238 | 74.99% | 65.18% | 0.615 | High accuracy, lower minority recall |
| **Decision Tree (Max Depth 8)** | 0.6254 | ±0.0178 | 65.84% | 63.83% | 1.947 | High variance |
| **K-Nearest Neighbors (k=17)** | 0.5574 | ±0.0158 | 68.10% | 55.51% | 1.224 | Sensitive to feature dimensionality |
| **Gaussian Naïve Bayes** | 0.2133 | ±0.0091 | 23.79% | 38.18% | 27.167 | Violated independence assumptions |

---

## 2. Final Held-Out Performance Metrics (885 Rows)

Evaluated once on the untouched stratified holdout test set:

- **Overall Accuracy:** `74.24%`
- **Macro-Averaged F1-Score:** `0.6074`
- **Weighted F1-Score:** `0.7032`
- **Balanced Accuracy (Mean Recall):** `61.86%`
- **Multiclass One-vs-Rest ROC-AUC:** `0.8555`
- **Test Log-Loss:** `0.6428`
- **Dropout Brier Score (Uncalibrated):** `0.1189`
- **Dropout Brier Score (Sigmoid Calibrated):** `0.1063` *(10.6% calibration error reduction)*

### Per-Class Detailed Diagnostic Breakdown

| Outcome Class | Holdout Support | Precision | Recall | F1-Score | OvR ROC-AUC | PR Average Precision |
|---|---|---|---|---|---|---|
| **Dropout** | 284 students (32.1%) | **76.37%** | **78.52%** | **0.7743** | **0.8984** | **0.8142** |
| **Enrolled** | 159 students (18.0%) | 47.83% | 13.84% | 0.2146 | 0.7252 | 0.3486 |
| **Graduate** | 442 students (49.9%) | 75.32% | 93.21% | 0.8332 | 0.8847 | 0.8655 |
| **Macro Average** | 885 students (100%) | 66.51% | 61.86% | 0.6074 | **0.8555** | 0.6761 |

---

## 3. Normalized Confusion Matrix

$$\begin{pmatrix} 
\text{Actual \ Predicted} & \text{Dropout} & \text{Enrolled} & \text{Graduate} \\
\text{Dropout (284)} & \mathbf{223\ (78.5\%)} & 13\ (4.6\%) & 48\ (16.9\%) \\
\text{Enrolled (159)} & 50\ (31.4\%) & \mathbf{22\ (13.8\%)} & 87\ (54.7\%) \\
\text{Graduate (442)} & 19\ (4.3\%) & 11\ (2.5\%) & \mathbf{412\ (93.2\%)}
\end{pmatrix}$$

**Clinical Interpretation:**
1. **Strong Separation on Extremes:** The model cleanly separates graduating students from dropouts (only 4.3% of true graduates are misclassified as dropouts, and 16.9% of dropouts are misclassified as graduates).
2. **The Intermediate 'Enrolled' Challenge:** 54.7% of enrolled students are classified as likely graduates, reflecting that active students with passing first-semester marks statistically resemble graduates until progression changes.

---

## 4. Operational Decision Threshold Analysis

In educational retention, an arbitrary 0.50 probability cutoff is often sub-optimal. The operational screening threshold was selected using **out-of-fold (OOF) training predictions** with a minimum precision target of 75%:

$$\text{Optimal Screening Threshold} = \mathbf{37.72\%}$$

### Operational Threshold Comparison (Held-Out Test Set)

| Threshold | Flagged Students | Recall (True Positives) | Precision | False Positives | False Negatives | Operational Fit |
|---|---|---|---|---|---|---|
| **0.25** | 352 (39.8%) | **88.0% (250)** | 71.0% | 102 | 34 | High advisor workload |
| **0.38 (Selected)** | **280 (31.6%)** | **79.9% (227)** | **74.2%** | **79** | **57** | **Optimal Caseload & Coverage** |
| **0.50 (Default)** | 197 (22.3%) | 59.5% (169) | 85.8% | 28 | 115 | Misses 115 vulnerable dropouts |
| **0.60** | 134 (15.1%) | 46.5% (132) | 98.5% | 2 | 152 | Severe under-screening |
| **0.75** | 56 (6.3%) | 19.4% (55) | 98.2% | 1 | 229 | Emergency cases only |

---

## 5. False Positive vs. False Negative Operational Costs

| Metric | False Positive (FP) | False Negative (FN) |
|---|---|---|
| **Count at 37.7% Threshold** | **79 students** | **57 students** |
| **Institutional Consequence** | Advisor conducts voluntary 30-minute academic consultation for a student who would have completed on their own. | Student quietly withdraws without ever receiving tutoring or emergency financial aid. |
| **Financial Cost** | ~\$40 in advisor labor per outreach. | Lost institutional tuition revenue (\$5,000–\$15,000/year) and student loan debt without degree. |
| **Student Impact** | Low / Positive (supportive check-in). | Severe / Critical (academic termination). |
| **Strategic Stance** | **Tolerate higher FP rate to minimize FN rate** via voluntary, supportive messaging. |

---

## 6. Exploratory Subgroup Disparity Audit

To audit algorithmic fairness, descriptive error rates were evaluated across demographic and socioeconomic slices on held-out data:

| Sensitive Attribute | Slice Group | Subgroup Size | Flag Rate | Dropout Recall | Dropout Precision | False Positive Rate |
|---|---|---|---|---|---|---|
| **Gender** | Female (0) | 563 rows | 27.4% | 76.5% | 81.2% | 6.8% |
| **Gender** | Male (1) | 322 rows | 38.8% | 83.2% | 78.4% | 8.9% |
| **Scholarship Holder** | Non-Holder (0) | 682 rows | 35.8% | 80.8% | 75.8% | 9.2% |
| **Scholarship Holder** | Holder (1) | 203 rows | 17.7% | 72.7% | 77.8% | 3.8% |
| **Displaced Student** | Living Locally (0) | 401 rows | 32.7% | 75.8% | 86.3% | 7.1% |
| **Displaced Student** | Displaced (1) | 484 rows | 23.1% | 65.9% | 79.5% | 6.6% |

> **Ethical Note:** Error rate variations between demographic slices reflect historical baseline differences in dropout incidence in the public dataset. Model outputs must be paired with human oversight to avoid compounding systemic educational disparities.
