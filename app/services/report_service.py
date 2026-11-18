"""Report Service: generates formal printable Academic Retention Dossiers in PDF and Markdown."""
from __future__ import annotations
import pandas as pd
from app.services.model_service import get_bundle, get_metrics
from app.services.prediction_service import prepare_student_record
from src.intelligence import generate_student_dossier, generate_student_dossier_pdf


def get_markdown_dossier(student_data: dict | pd.DataFrame, case_ref: str = "DEMO-001", advisor_name: str = "Academic Advisor") -> str:
    bundle = get_bundle()
    metrics = get_metrics()
    record = prepare_student_record(student_data)
    return generate_student_dossier(bundle, metrics, record, case_ref=case_ref, advisor_name=advisor_name)


def get_pdf_dossier(student_data: dict | pd.DataFrame, case_ref: str = "DEMO-001", advisor_name: str = "Academic Advisor") -> bytes:
    bundle = get_bundle()
    metrics = get_metrics()
    record = prepare_student_record(student_data)
    return generate_student_dossier_pdf(bundle, metrics, record, case_ref=case_ref, advisor_name=advisor_name)
