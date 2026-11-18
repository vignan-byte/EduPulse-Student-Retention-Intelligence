import numpy as np
import pandas as pd
import pytest

from src.intelligence import (
    recommendations,
    screen_cohort,
    counterfactual_recourse,
    advisor_capacity_planner,
    generate_student_dossier,
    generate_student_dossier_pdf,
    get_preset_student_profiles,
    compute_cohort_heatmap,
)
from src.ml import load_data


class DummyBundle:
    def __init__(self):
        self.classes_ = np.array(["Dropout", "Enrolled", "Graduate"])

    def predict_proba(self, X):
        # High dropout probability if approved units < 3 or debtor
        probs = []
        for _, row in X.iterrows():
            approved = row.get("Curricular units 1st sem (approved)", 0)
            debtor = row.get("Debtor", 0)
            if approved < 3 or debtor == 1:
                probs.append([0.65, 0.15, 0.20])
            else:
                probs.append([0.18, 0.22, 0.60])
        return np.array(probs)


@pytest.fixture
def dummy_bundle():
    return {
        "features": [
            "Curricular units 1st sem (enrolled)",
            "Curricular units 1st sem (approved)",
            "Curricular units 1st sem (grade)",
            "Debtor",
            "Tuition fees up to date",
            "Admission grade",
        ],
        "model": DummyBundle(),
        "stage": "After semester 1",
    }


def test_preset_profiles_exist():
    presets = get_preset_student_profiles()
    assert "High Risk (Academic Difficulty & Tuition Arrears)" in presets
    assert "Low Risk / Dean's List (Scholarship Holder)" in presets
    for name, profile in presets.items():
        assert "Curricular units 1st sem (approved)" in profile


def test_counterfactual_recourse_for_high_risk(dummy_bundle):
    record = pd.DataFrame([{
        "Curricular units 1st sem (enrolled)": 6.0,
        "Curricular units 1st sem (approved)": 1.0,
        "Curricular units 1st sem (grade)": 9.5,
        "Debtor": 1,
        "Tuition fees up to date": 0,
        "Admission grade": 110.0,
    }])
    recourse = counterfactual_recourse(dummy_bundle, record, target_threshold=0.35)
    assert recourse["current_risk"] == 0.65
    assert len(recourse["actionable_steps"]) > 0
    assert recourse["projected_risk"] < 0.65


def test_counterfactual_recourse_for_low_risk(dummy_bundle):
    record = pd.DataFrame([{
        "Curricular units 1st sem (enrolled)": 6.0,
        "Curricular units 1st sem (approved)": 6.0,
        "Curricular units 1st sem (grade)": 15.0,
        "Debtor": 0,
        "Tuition fees up to date": 1,
        "Admission grade": 140.0,
    }])
    recourse = counterfactual_recourse(dummy_bundle, record, target_threshold=0.35)
    assert recourse["status"] == "Already on track"
    assert recourse["current_risk"] < 0.35


def test_advisor_capacity_planner():
    metrics = {
        "test_rows": 885,
        "threshold_scenarios": [
            {"threshold": 0.25, "precision": 0.65, "recall": 0.88, "flagged_count": 320},
            {"threshold": 0.38, "precision": 0.74, "recall": 0.80, "flagged_count": 230},
            {"threshold": 0.50, "precision": 0.82, "recall": 0.62, "flagged_count": 160},
        ],
    }
    planner = advisor_capacity_planner(
        metrics, total_students=1000, advisor_count=4, max_caseload=50, avg_tuition=5000.0
    )
    assert planner["total_advisor_capacity"] == 200
    assert planner["recommended_threshold"] in (0.25, 0.38, 0.50)
    assert len(planner["scenarios"]) == 3
    assert planner["recommended_scenario"]["estimated_tuition_preserved"] >= 0


def test_generate_student_dossier(dummy_bundle):
    record = pd.DataFrame([{
        "Curricular units 1st sem (enrolled)": 6.0,
        "Curricular units 1st sem (approved)": 1.0,
        "Curricular units 1st sem (grade)": 9.5,
        "Debtor": 1,
        "Tuition fees up to date": 0,
        "Admission grade": 110.0,
        "Scholarship holder": 0,
    }])
    metrics = {"selected_screening_threshold": 0.38}
    dossier = generate_student_dossier(dummy_bundle, metrics, record, case_ref="DEMO-TEST-99")
    assert "DEMO-TEST-99" in dossier
    assert "Academic Retention & Support Dossier" in dossier
    assert "Actionable Counterfactual Recourse" in dossier


def test_generate_student_dossier_pdf(dummy_bundle):
    record = pd.DataFrame([{
        "Curricular units 1st sem (enrolled)": 6.0,
        "Curricular units 1st sem (approved)": 1.0,
        "Curricular units 1st sem (grade)": 9.5,
        "Debtor": 1,
        "Tuition fees up to date": 0,
        "Admission grade": 110.0,
        "Scholarship holder": 0,
    }])
    metrics = {"selected_screening_threshold": 0.38}
    pdf_bytes = generate_student_dossier_pdf(dummy_bundle, metrics, record, case_ref="DEMO-PDF-99")
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 500


def test_compute_cohort_heatmap():
    df = load_data("data/students.csv")
    for dim in ("academics", "financial", "scholarship"):
        res = compute_cohort_heatmap(df, dim)
        assert "rate_matrix" in res
        assert "count_matrix" in res
        assert res["total_students"] == 4424
        assert res["rate_matrix"].shape[0] > 0
        assert res["rate_matrix"].shape[1] > 0
