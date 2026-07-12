"""Write rejected rows to CSV under datasets rejected folder."""

from __future__ import annotations

import csv
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.config import get_settings


def write_rejects(entity: str, rows: list[dict[str, Any]]) -> Path | None:
    """Persist reject file; return path or None if no rows."""
    if not rows:
        return None

    settings = get_settings()
    reject_dir = settings.datasets_path / "rejected"
    reject_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    path = reject_dir / f"{stamp}_{entity}.csv"

    # union of keys
    fieldnames: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for k in row:
            if k not in seen:
                seen.add(k)
                fieldnames.append(k)

    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    return path
