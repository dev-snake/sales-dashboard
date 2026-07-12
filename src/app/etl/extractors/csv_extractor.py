"""CSV file extractor."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from loguru import logger


class CsvExtractor:
    """Read CSV with UTF-8 then latin-1 fallback."""

    def extract(self, path: Path) -> pd.DataFrame:
        path = Path(path)
        if not path.is_file():
            raise FileNotFoundError(f"CSV not found: {path}")

        try:
            df = pd.read_csv(path, dtype=str, keep_default_na=False)
            logger.info("Extracted CSV | path={} rows={} cols={}", path, len(df), len(df.columns))
            return df
        except UnicodeDecodeError:
            logger.warning("UTF-8 failed for {}, retrying latin-1", path)
            df = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="latin-1")
            logger.info("Extracted CSV (latin-1) | path={} rows={}", path, len(df))
            return df
