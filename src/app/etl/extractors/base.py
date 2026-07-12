"""Extractor protocol and shared helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol

import pandas as pd


class Extractor(Protocol):
    def extract(self, path: Path) -> pd.DataFrame: ...


def dataframe_to_records(df: pd.DataFrame) -> list[dict[str, Any]]:
    """Convert DataFrame to list of plain dicts with NaN → None."""
    if df.empty:
        return []
    cleaned = df.where(pd.notna(df), None)
    records: list[dict[str, Any]] = [
        {str(k): v for k, v in row.items()} for row in cleaned.to_dict(orient="records")
    ]
    return records
