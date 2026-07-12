"""Excel (.xlsx) extractor."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from loguru import logger


class ExcelExtractor:
    """Read first sheet (or named sheet) as strings."""

    def __init__(self, sheet_name: str | int = 0) -> None:
        self.sheet_name = sheet_name

    def extract(self, path: Path) -> pd.DataFrame:
        path = Path(path)
        if not path.is_file():
            raise FileNotFoundError(f"Excel not found: {path}")

        df = pd.read_excel(path, sheet_name=self.sheet_name, dtype=str)
        df = df.fillna("")
        logger.info(
            "Extracted Excel | path={} sheet={} rows={} cols={}",
            path,
            self.sheet_name,
            len(df),
            len(df.columns),
        )
        return df
