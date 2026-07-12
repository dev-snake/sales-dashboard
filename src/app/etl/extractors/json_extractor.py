"""JSON file extractor."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
from loguru import logger


class JsonExtractor:
    """Read JSON list of objects or ``{\"records\": [...]}``."""

    def extract(self, path: Path) -> pd.DataFrame:
        path = Path(path)
        if not path.is_file():
            raise FileNotFoundError(f"JSON not found: {path}")

        with path.open(encoding="utf-8") as fh:
            payload: Any = json.load(fh)

        if isinstance(payload, dict):
            if "records" in payload:
                payload = payload["records"]
            elif "data" in payload:
                payload = payload["data"]
            else:
                # single object → one row
                payload = [payload]

        if not isinstance(payload, list):
            raise ValueError(f"Unsupported JSON structure in {path}")

        df = pd.DataFrame(payload)
        # normalize all to string for consistent cleaning
        df = df.astype(str).replace({"None": "", "nan": "", "NaT": ""})
        logger.info("Extracted JSON | path={} rows={}", path, len(df))
        return df
