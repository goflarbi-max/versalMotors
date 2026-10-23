"""Stable JSON conversion for pandas results without NaN leakage."""

from __future__ import annotations

import math
from datetime import date, datetime
from typing import Any

import pandas as pd


def json_value(value: Any) -> Any:
    if value is None or value is pd.NA:
        return None
    if isinstance(value, (pd.Timestamp, datetime, date)):
        return value.isoformat()
    if hasattr(value, "item") and not isinstance(value, (str, bytes, dict, list, tuple)):
        try:
            value = value.item()
        except ValueError:
            pass
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    if isinstance(value, dict):
        return {str(key): json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_value(item) for item in value]
    return value


def frame_records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    return [json_value(record) for record in frame.to_dict(orient="records")]
