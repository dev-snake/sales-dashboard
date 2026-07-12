"""YAML/JSON-ish manifest for multi-entity ETL (simple format without PyYAML dep).

Supports a minimal YAML subset:

```yaml
ensure_sample_masters: true
jobs:
  - entity: customers
    path: datasets/raw/samples/customers.csv
  - entity: products
    path: datasets/raw/samples/products.xlsx
```
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from app.config.settings import PROJECT_ROOT
from app.utils.errors import ETLError


@dataclass(frozen=True, slots=True)
class ManifestJob:
    entity: str
    path: Path


@dataclass(frozen=True, slots=True)
class Manifest:
    jobs: list[ManifestJob]
    ensure_sample_masters: bool = False


def load_manifest(path: Path) -> Manifest:
    path = Path(path)
    if not path.is_file():
        raise ETLError(f"Manifest not found: {path}")

    text = path.read_text(encoding="utf-8")
    ensure = False
    jobs: list[ManifestJob] = []
    current_entity: str | None = None
    current_path: str | None = None

    for raw in text.splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        if re.match(r"^ensure_sample_masters\s*:", line):
            val = line.split(":", 1)[1].strip().lower()
            ensure = val in {"true", "yes", "1"}
            continue
        if line.strip() == "jobs:":
            continue
        m_ent = re.match(r"^\s*-\s*entity\s*:\s*(.+)$", line)
        if m_ent:
            # flush previous
            if current_entity and current_path:
                jobs.append(_job(current_entity, current_path, path.parent))
            current_entity = m_ent.group(1).strip().strip("\"'")
            current_path = None
            continue
        m_path = re.match(r"^\s*path\s*:\s*(.+)$", line)
        if m_path and current_entity:
            current_path = m_path.group(1).strip().strip("\"'")
            continue

    if current_entity and current_path:
        jobs.append(_job(current_entity, current_path, path.parent))

    if not jobs:
        raise ETLError(f"No jobs found in manifest: {path}")
    return Manifest(jobs=jobs, ensure_sample_masters=ensure)


def _job(entity: str, raw_path: str, manifest_dir: Path) -> ManifestJob:
    p = Path(raw_path)
    if not p.is_absolute():
        # try relative to project root, then manifest dir
        cand = PROJECT_ROOT / p
        if not cand.is_file():
            cand = manifest_dir / p
        p = cand
    return ManifestJob(entity=entity.strip().lower(), path=p)


def default_samples_manifest() -> Manifest:
    """Built-in job list for datasets/raw/samples (no file required)."""
    samples = PROJECT_ROOT / "datasets" / "raw" / "samples"
    return Manifest(
        ensure_sample_masters=True,
        jobs=[
            ManifestJob("customers", samples / "customers.csv"),
            ManifestJob("products", samples / "products.xlsx"),
            ManifestJob("orders", samples / "orders.csv"),
            ManifestJob("order_items", samples / "order_items.csv"),
            ManifestJob("payments", samples / "payments.json"),
        ],
    )
