"""Leakage-conscious student outcome modeling on the UCI 697 dataset."""
from __future__ import annotations

import json
import hashlib
import platform
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier, StackingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import (accuracy_score, balanced_accuracy_score, brier_score_loss,
                             classification_report, confusion_matrix, f1_score, log_loss,
                             precision_recall_curve, average_precision_score, roc_auc_score,
                             roc_curve)
from sklearn.model_selection import (StratifiedKFold, cross_validate, cross_val_predict,
                                     train_test_split, RandomizedSearchCV)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

DATA_URL = "https://archive.ics.uci.edu/static/public/697/data.csv"
TARGET = "Target"
FEATURE_SCHEMA = ['Marital Status', 'Application mode', 'Application order', 'Course', 'Daytime/evening attendance', 'Previous qualification', 'Previous qualification (grade)', 'Nacionality', "Mother's qualification", "Father's qualification", "Mother's occupation", "Father's occupation", 'Admission grade', 'Displaced', 'Educational special needs', 'Debtor', 'Tuition fees up to date', 'Gender', 'Scholarship holder', 'Age at enrollment', 'International', 'Curricular units 1st sem (credited)', 'Curricular units 1st sem (enrolled)', 'Curricular units 1st sem (evaluations)', 'Curricular units 1st sem (approved)', 'Curricular units 1st sem (grade)', 'Curricular units 1st sem (without evaluations)', 'Curricular units 2nd sem (credited)', 'Curricular units 2nd sem (enrolled)', 'Curricular units 2nd sem (evaluations)', 'Curricular units 2nd sem (approved)', 'Curricular units 2nd sem (grade)', 'Curricular units 2nd sem (without evaluations)', 'Unemployment rate', 'Inflation rate', 'GDP']
OUTCOMES = ["Dropout", "Enrolled", "Graduate"]
STAGES = {"Admission": 0, "After semester 1": 1, "After semester 2": 2}
CAT_COLS = ["Marital Status", "Application mode", "Application order", "Course",
            "Daytime/evening attendance", "Previous qualification", "Nacionality",
            "Mother's qualification", "Father's qualification", "Mother's occupation",
            "Father's occupation", "Displaced", "Educational special needs", "Debtor",
            "Tuition fees up to date", "Gender", "Scholarship holder", "International"]


def load_data(path: str | Path = "data/students.csv", download: bool = False) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        if not download:
            raise FileNotFoundError(f"Dataset missing at {path}. Run python -m src.train --download")
        path.parent.mkdir(parents=True, exist_ok=True)
        # Trust the published UCI archive, not synthetic data or an unknown mirror.
        from urllib.request import urlopen
        with urlopen(DATA_URL, timeout=30) as response:
            content = response.read()
        path.write_bytes(content)
    # UCI 697 is comma-separated. Explicit delimiter avoids the CSV sniffer
    # misclassifying legitimate one-column test inputs or malformed files.
    df = pd.read_csv(path, sep=",", encoding="utf-8-sig")
    df.columns = df.columns.str.strip()
    if TARGET not in df:
        raise ValueError("Expected UCI dataset with a 'Target' column")
    labels = set(df[TARGET].dropna().astype(str).str.strip())
    if df[TARGET].isna().any() or not labels <= set(OUTCOMES) or not labels:
        raise ValueError(f"Unexpected target labels: {sorted(labels)}")
    if df.columns.duplicated().any():
        raise ValueError("Duplicate feature names are not supported")
    return df


def stage_features(df: pd.DataFrame, stage: str) -> pd.DataFrame:
    if stage not in STAGES:
        raise ValueError(f"Unknown stage: {stage}")
    unknown = set(df.columns) - set(FEATURE_SCHEMA) - {TARGET}
    if unknown:
        raise ValueError(f"Unknown or potentially post-outcome fields: {sorted(unknown)}")
    X = df.drop(columns=[TARGET], errors="ignore").copy()
    # Reject post-prediction fields rather than let future grades leak into an early model.
    if STAGES[stage] < 2:
        X = X.loc[:, ~X.columns.str.contains(r"2nd sem", case=False, regex=True)]
    if STAGES[stage] < 1:
        X = X.loc[:, ~X.columns.str.contains(r"1st sem", case=False, regex=True)]
    return X


def make_pipeline(X: pd.DataFrame, algorithm: str = "logistic") -> Pipeline:
    categorical = [c for c in CAT_COLS if c in X.columns]
    numeric = [c for c in X if c not in categorical]
    # Small UCI dataset: dense encoding keeps GaussianNB compatible with the
    # same preprocessing design used by every other benchmark classifier.
    encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    preprocessor = ColumnTransformer([
        ("numeric", Pipeline([("impute", SimpleImputer(strategy="median")),
                               ("scale", StandardScaler())]), numeric),
        ("categorical", Pipeline([("impute", SimpleImputer(strategy="most_frequent")),
                                   ("encode", encoder)]), categorical),
    ])
    models = {
        "logistic": LogisticRegression(max_iter=1500, class_weight="balanced", random_state=42),
        "forest": RandomForestClassifier(n_estimators=250, min_samples_leaf=3,
                                         class_weight="balanced_subsample", random_state=42, n_jobs=-1),
        "boosting": GradientBoostingClassifier(random_state=42),
        "tree": DecisionTreeClassifier(max_depth=8, min_samples_leaf=8,
                                       class_weight="balanced", random_state=42),
        "knn": KNeighborsClassifier(n_neighbors=17, weights="distance"),
        "svm": SVC(C=1.0, kernel="rbf", class_weight="balanced", probability=True, random_state=42),
        "naive_bayes": GaussianNB(),
        "stacking": StackingClassifier(
            estimators=[
                ("lr", LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)),
                ("rf", RandomForestClassifier(n_estimators=100, min_samples_leaf=3,
                                              class_weight="balanced_subsample", random_state=42, n_jobs=-1)),
                ("gb", GradientBoostingClassifier(n_estimators=100, random_state=42)),
            ],
            final_estimator=LogisticRegression(max_iter=1000, random_state=42),
            cv=3,
            n_jobs=-1,
        ),
    }
    if algorithm not in models:
        raise ValueError(f"Unknown model: {algorithm}")
    return Pipeline([("preprocess", preprocessor), ("model", models[algorithm])])


def dropout_diagnostics(y_true, probabilities, classes, threshold=0.5):
    """Binary screening diagnostics; does not collapse 'Enrolled' for multiclass training."""
    if "Dropout" not in classes:
        raise ValueError("Dropout class is required")
    scores = np.asarray(probabilities)[:, list(classes).index("Dropout")]
    actual = (np.asarray(y_true) == "Dropout").astype(int)
    flagged = (scores >= threshold).astype(int)
    tp = int(((actual == 1) & (flagged == 1)).sum())
    fn = int(((actual == 1) & (flagged == 0)).sum())
    fp = int(((actual == 0) & (flagged == 1)).sum())
    tn = int(((actual == 0) & (flagged == 0)).sum())
    bins = np.linspace(0, 1, 11)
    expected_error = 0.0
    for i in range(10):
        included = (scores >= bins[i]) & ((scores < bins[i+1]) if i < 9 else (scores <= bins[i+1]))
        if included.any():
            expected_error += float(included.mean() * abs(actual[included].mean() - scores[included].mean()))
    return {"threshold": threshold, "tp": tp, "fn": fn, "fp": fp, "tn": tn,
            "precision": tp / (tp + fp) if tp + fp else 0.0,
            "recall": tp / (tp + fn) if tp + fn else 0.0,
            "brier_score": float(brier_score_loss(actual, scores)),
            "expected_calibration_error_10bin": expected_error,
            "average_precision": float(average_precision_score(actual, scores)),
            "flagged_count": int(flagged.sum())}


def subgroup_diagnostics(X_test, y_test, prob, classes, field, min_group=30,
                         min_positives=10, min_negatives=10):
    """Descriptive error-rate slices for auditing, not a guarantee of fairness."""
    if field not in X_test:
        return []
    output = []
    for group, positions in X_test.groupby(field, dropna=False).indices.items():
        if len(positions) < min_group:
            continue
        y_slice = np.asarray(y_test)[positions]
        positives = int((y_slice == "Dropout").sum())
        negatives = len(y_slice) - positives
        if positives < min_positives or negatives < min_negatives:
            continue
        selected = np.asarray(prob)[positions]
        d = dropout_diagnostics(y_slice, selected, classes)
        output.append({"group": str(group), "count": len(positions),
                       "dropout_count": positives, "non_dropout_count": negatives,
                       "dropout_recall": d["recall"], "flag_rate": d["flagged_count"] / len(positions),
                       "false_positive_rate": d["fp"] / negatives,
                       "dropout_precision": d["precision"],
                       "false_positive_count": d["fp"]})
    return output


def choose_screening_threshold(y_true, dropout_scores, minimum_precision=0.75):
    """Pick a review threshold from OOF training predictions only.

    Among thresholds satisfying the minimum precision constraint, maximize
    recall; if none qualify, return the F2-optimal point. This is a research
    operating point, not a deployment policy.
    """
    actual = (np.asarray(y_true) == "Dropout").astype(int)
    scores = np.asarray(dropout_scores, dtype=float)
    if len(scores) != len(actual) or len(scores) == 0 or not np.isfinite(scores).all():
        raise ValueError("Invalid screening scores")
    precision, recall, thresholds = precision_recall_curve(actual, scores)
    eligible = np.where((precision[:-1] >= minimum_precision) & (recall[:-1] > 0))[0]
    if len(eligible):
        index = sorted(eligible, key=lambda i: (-recall[i], -precision[i], thresholds[i]))[0]
    else:
        f2 = 5 * precision[:-1] * recall[:-1] / np.maximum(4 * precision[:-1] + recall[:-1], 1e-12)
        index = int(np.argmax(f2))
    return float(thresholds[index]), {"oof_precision": float(precision[index]),
                                      "oof_recall": float(recall[index]),
                                      "minimum_precision_target": minimum_precision,
                                      "met_precision_target": bool(len(eligible))}


def train_and_evaluate(df: pd.DataFrame, stage: str, tune: bool = False,
                       full_benchmark: bool = False, calibrate: bool = True):
    X = stage_features(df, stage)
    y = df[TARGET].astype(str).str.strip()
    if y.isna().any() or y.value_counts().min() < 5:
        raise ValueError("Need at least five examples per outcome class")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    comparisons = []
    candidates = ("logistic", "forest", "boosting", "tree", "knn", "svm", "naive_bayes", "stacking") if full_benchmark else ("logistic", "forest", "boosting")
    for name in candidates:
        pipe = make_pipeline(X_train, name)
        scores = cross_validate(pipe, X_train, y_train, cv=cv, scoring={"macro_f1": "f1_macro", "accuracy": "accuracy", "balanced_accuracy": "balanced_accuracy", "log_loss": "neg_log_loss"}, n_jobs=1)
        comparisons.append({"model": name, "cv_macro_f1_mean": float(scores["test_macro_f1"].mean()),
                            "cv_macro_f1_std": float(scores["test_macro_f1"].std()),
                            "cv_accuracy": float(scores["test_accuracy"].mean()),
                            "cv_balanced_accuracy": float(scores["test_balanced_accuracy"].mean()),
                            "cv_log_loss": float(-scores["test_log_loss"].mean())})
    comparisons.sort(key=lambda r: r["cv_macro_f1_mean"], reverse=True)
    winner = comparisons[0]["model"]
    model = make_pipeline(X_train, winner)
    tuning = None
    if tune:
        spaces = {
            "logistic": {"model__C": [.1, 1., 10.]},
            "forest": {"model__max_depth": [None, 12], "model__min_samples_leaf": [3, 8]},
            "boosting": {"model__learning_rate": [.03, .1], "model__max_depth": [2, 3]},
            "tree": {"model__max_depth": [4, 8, 12]},
            "knn": {"model__n_neighbors": [9, 17, 31]},
            "svm": {"model__C": [.1, 1., 10.]},
            "naive_bayes": {"model__var_smoothing": [1e-9, 1e-7, 1e-5]},
            "stacking": {"model__final_estimator__C": [.1, 1., 10.]},
        }
        search = RandomizedSearchCV(model, spaces.get(winner, {"model__C": [1.]}), n_iter=3,
                    scoring="f1_macro", cv=cv, random_state=42, n_jobs=1)
        search.fit(X_train, y_train)
        model = search.best_estimator_
        tuning = {"parameters": search.best_params_, "cv_macro_f1": float(search.best_score_),
                  "trials": [{"parameters": p, "cv_macro_f1": float(v)} for p, v in
                             zip(search.cv_results_["params"], search.cv_results_["mean_test_score"])]}
    else:
        model.fit(X_train, y_train)
    baseline_prob = model.predict_proba(X_test)
    baseline_classes = list(model.classes_)
    if calibrate:
        # Internal CV separates calibration fitting from each base estimator's
        # fit; no held-out test rows participate in model/calibrator training.
        calibrated = CalibratedClassifierCV(model, method="sigmoid", cv=3)
        calibrated.fit(X_train, y_train)
        model = calibrated
    # Out-of-fold training-only threshold selection; independent test remains
    # untouched until the operating point is fixed.
    threshold_cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=91)
    oof_prob = cross_val_predict(model, X_train, y_train, cv=threshold_cv,
                                method="predict_proba", n_jobs=1)
    threshold, oof_selection = choose_screening_threshold(
        y_train, oof_prob[:, list(model.classes_).index("Dropout")])
    pred = model.predict(X_test)
    prob = model.predict_proba(X_test)
    classes = list(model.classes_)
    
    # Calculate Multiclass OvR ROC Curves
    roc_curves = {}
    pr_curves = {}
    for c in classes:
        c_idx = classes.index(c)
        y_binary = (np.asarray(y_test) == c).astype(int)
        
        # ROC Curve
        fpr, tpr, _ = roc_curve(y_binary, prob[:, c_idx])
        auc_val = float(roc_auc_score(y_binary, prob[:, c_idx]))
        step = max(1, len(fpr) // 30)
        idx = list(range(0, len(fpr), step))
        if len(fpr) - 1 not in idx:
            idx.append(len(fpr) - 1)
        roc_curves[c] = {
            "fpr": [float(fpr[i]) for i in idx],
            "tpr": [float(tpr[i]) for i in idx],
            "auc": round(auc_val, 4)
        }
        
        # Precision-Recall Curve
        prec, rec, _ = precision_recall_curve(y_binary, prob[:, c_idx])
        ap_val = float(average_precision_score(y_binary, prob[:, c_idx]))
        step_pr = max(1, len(prec) // 30)
        idx_pr = list(range(0, len(prec), step_pr))
        if len(prec) - 1 not in idx_pr:
            idx_pr.append(len(prec) - 1)
        pr_curves[c] = {
            "precision": [float(prec[i]) for i in idx_pr],
            "recall": [float(rec[i]) for i in idx_pr],
            "avg_precision": round(ap_val, 4)
        }

    # Calibration Curve (Reliability Diagram) for Dropout
    dropout_idx = classes.index("Dropout")
    y_drop_binary = (np.asarray(y_test) == "Dropout").astype(int)
    f_cal, p_cal = calibration_curve(y_drop_binary, prob[:, dropout_idx], n_bins=8)
    f_uncal, p_uncal = calibration_curve(y_drop_binary, baseline_prob[:, baseline_classes.index("Dropout")], n_bins=8)
    
    calibration_data = {
        "calibrated_prob_pred": [float(x) for x in p_cal],
        "calibrated_prob_true": [float(x) for x in f_cal],
        "uncalibrated_prob_pred": [float(x) for x in p_uncal],
        "uncalibrated_prob_true": [float(x) for x in f_uncal]
    }

    metrics = {
        "stage": stage, "selected_model": winner, "train_rows": len(X_train),
        "test_rows": len(X_test), "features": list(X.columns),
        "classes": classes, "accuracy": float(accuracy_score(y_test, pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_test, pred)),
        "macro_f1": float(f1_score(y_test, pred, average="macro")),
        "weighted_f1": float(f1_score(y_test, pred, average="weighted")),
        "log_loss": float(log_loss(y_test, prob, labels=classes)),
        "confusion_matrix": confusion_matrix(y_test, pred, labels=classes).tolist(),
        "classification_report": classification_report(y_test, pred, output_dict=True, zero_division=0),
        "model_comparison": comparisons,
        "calibrated": bool(calibrate),
        "hyperparameter_search": tuning,
        "uncalibrated_test_dropout_brier": float(brier_score_loss(
            (np.asarray(y_test) == "Dropout").astype(int),
            baseline_prob[:, baseline_classes.index("Dropout")])),
        "selected_screening_threshold": threshold,
        "threshold_selection_training_oof": oof_selection,
        "selected_threshold_test_diagnostics": dropout_diagnostics(y_test, prob, classes, threshold),
        "dropout_screening_at_0_5": dropout_diagnostics(y_test, prob, classes),
        "threshold_scenarios": [dropout_diagnostics(y_test, prob, classes, t) for t in (0.25, 0.4, 0.5, 0.6, 0.75)],
        "subgroup_audit": {col: subgroup_diagnostics(X_test, y_test, prob, classes, col)
                           for col in ("Gender", "Scholarship holder", "Displaced") if col in X_test},
        "roc_curve_data": roc_curves,
        "pr_curve_data": pr_curves,
        "calibration_curve_data": calibration_data,
        "dataset_source": DATA_URL,
        "random_state": 42,
        "training_fingerprint_sha256": hashlib.sha256(
            pd.util.hash_pandas_object(df, index=True).values.tobytes()).hexdigest(),
        "environment": {"python": platform.python_version(),
                        "scikit_learn": sklearn.__version__, "pandas": pd.__version__},
    }
    try:
        metrics["multiclass_roc_auc_ovr"] = float(roc_auc_score(
            y_test, prob, multi_class="ovr", average="macro", labels=classes))
    except ValueError:
        metrics["multiclass_roc_auc_ovr"] = None
    return model, metrics


def save_bundle(model: Pipeline, metrics: dict, destination: str | Path):
    dest = Path(destination)
    dest.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": model, "stage": metrics["stage"],
                 "features": metrics["features"], "classes": metrics["classes"]}, dest / "model.joblib")
    (dest / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    from .registry import write_manifest
    write_manifest(dest)


def predict_student(bundle: dict, record: pd.DataFrame) -> pd.DataFrame:
    if len(record) != 1:
        raise ValueError("Provide exactly one student record")
    needed = bundle["features"]
    missing = set(needed) - set(record.columns)
    if missing:
        raise ValueError(f"Missing model features: {sorted(missing)}")
    probabilities = bundle["model"].predict_proba(record[needed])[0]
    return pd.DataFrame({"outcome": bundle["model"].classes_, "probability": probabilities})
