"""Input and export safeguards for a LOCAL educational demonstration.

These are deliberately not presented as real-world privacy compliance.
"""
from __future__ import annotations

import re
from io import BytesIO
import pandas as pd

MAX_UPLOAD_BYTES = 250_000


def read_anonymous_record(upload, features: list[str], max_rows: int = 1) -> pd.DataFrame:
    """Accept one bounded tabular record and reject obvious identity columns."""
    raw = upload.read(MAX_UPLOAD_BYTES + 1)
    if len(raw) > MAX_UPLOAD_BYTES:
        raise ValueError("CSV exceeds the 250 KB demo input limit")
    try:
        frame = pd.read_csv(BytesIO(raw))
    except Exception as exc:
        raise ValueError("Invalid CSV file") from exc
    if len(frame) < 1 or len(frame) > max_rows:
        raise ValueError("Upload exactly one anonymized student row" if max_rows == 1 else f"Upload 1 to {max_rows} rows")
    identity_patterns = re.compile(r"(^|[_\s-])(name|email|phone|mobile|address|roll[_\s-]*no|student[_\s-]*id|aadhaar)([_\s-]|$)", re.I)
    if any(identity_patterns.search(str(c)) for c in frame.columns):
        raise ValueError("Potentially identifying column detected; remove it before upload")
    missing = set(features) - set(frame.columns)
    if missing:
        raise ValueError(f"Missing required feature columns: {sorted(missing)[:6]}")
    extra = set(frame.columns) - set(features)
    if extra:
        raise ValueError(f"Unexpected columns: {sorted(extra)}")
    import numpy as np
    try:
        frame = frame[features].apply(pd.to_numeric, errors="raise")
    except (ValueError, TypeError) as exc:
        raise ValueError("Features must contain numeric UCI codes") from exc
    if np.isinf(frame.to_numpy(dtype=float)).any():
        raise ValueError("Infinite values are not supported")
    if frame[features].isna().all(axis=1).any():
        raise ValueError("Input is entirely empty")
    return frame[features]


def validate_demo_reference(value: str) -> bool:
    return re.fullmatch(r"DEMO-[A-Za-z0-9-]{1,24}", value) is not None
