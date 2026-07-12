"""ETL run result types."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class EtlResult:
    """Summary of one entity ETL run."""

    entity: str
    source_path: Path
    rows_read: int = 0
    rows_valid: int = 0
    rows_rejected: int = 0
    rows_loaded: int = 0
    reject_path: Path | None = None
    errors: list[str] = field(default_factory=list)
    duration_seconds: float = 0.0

    @property
    def status(self) -> str:
        if self.errors and self.rows_loaded == 0:
            return "failed"
        if self.rows_rejected > 0:
            return "partial"
        return "success"
