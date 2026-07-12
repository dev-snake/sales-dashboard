"""Pick extractor from file extension."""

from __future__ import annotations

from pathlib import Path

from app.etl.extractors.csv_extractor import CsvExtractor
from app.etl.extractors.excel_extractor import ExcelExtractor
from app.etl.extractors.json_extractor import JsonExtractor
from app.utils.errors import ETLError


def get_extractor(path: Path) -> CsvExtractor | ExcelExtractor | JsonExtractor:
    suffix = Path(path).suffix.lower()
    if suffix == ".csv":
        return CsvExtractor()
    if suffix in {".xlsx", ".xlsm"}:
        return ExcelExtractor()
    if suffix == ".json":
        return JsonExtractor()
    raise ETLError(f"Unsupported file type: {suffix}", details={"path": str(path)})
