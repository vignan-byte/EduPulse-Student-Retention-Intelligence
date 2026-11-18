from io import BytesIO
import pandas as pd
import pytest

from src.safety import read_anonymous_record, validate_demo_reference


def test_valid_csv():
    record = read_anonymous_record(BytesIO(b"Course,Age at enrollment\n2,21\n"),
                                   ["Course", "Age at enrollment"])
    assert record.shape == (1, 2)


def test_identity_columns_rejected():
    with pytest.raises(ValueError, match="identifying"):
        read_anonymous_record(BytesIO(b"student_id,Course\n123,2\n"), ["Course"])


def test_multiple_rows_rejected():
    with pytest.raises(ValueError, match="exactly one"):
        read_anonymous_record(BytesIO(b"Course\n1\n2\n"), ["Course"])


def test_demo_reference_validation():
    assert validate_demo_reference("DEMO-001")
    assert not validate_demo_reference("STUDENT-123")
