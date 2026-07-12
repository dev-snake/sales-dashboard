"""Discover and load SQL catalog files under project ``sql/``."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from app.config.settings import PROJECT_ROOT

LEVEL_DIRS = ("basic", "intermediate", "advanced", "reporting", "optimization")
_HEADER_RE = re.compile(r"^--\s*([A-Za-z]+):\s*(.*)$")


@dataclass(frozen=True, slots=True)
class SqlEntry:
    """One catalog query file."""

    id: str
    title: str
    skills: str
    tables: str
    params: str
    level: str
    path: Path
    sql: str


def sql_root() -> Path:
    return PROJECT_ROOT / "sql"


def list_entries(*, level: str | None = None) -> list[SqlEntry]:
    """Return all catalog entries, optionally filtered by level folder name."""
    root = sql_root()
    dirs = (level,) if level else LEVEL_DIRS
    entries: list[SqlEntry] = []
    for d in dirs:
        folder = root / d
        if not folder.is_dir():
            continue
        for path in sorted(folder.glob("*.sql")):
            entries.append(_parse_file(path, default_level=d))
    entries.sort(key=lambda e: (e.level, e.id))
    return entries


def load_entry(query_id: str) -> SqlEntry:
    """Load a single entry by ID (e.g. ``R04``, ``b01``)."""
    needle = query_id.strip().upper()
    for entry in list_entries():
        if entry.id.upper() == needle:
            return entry
    known = ", ".join(e.id for e in list_entries()[:10])
    raise KeyError(f"Unknown SQL id {query_id!r}. Examples: {known}, …")


def _parse_file(path: Path, *, default_level: str) -> SqlEntry:
    text = path.read_text(encoding="utf-8")
    meta: dict[str, str] = {}
    body_lines: list[str] = []
    in_header = True
    for line in text.splitlines():
        if in_header:
            m = _HEADER_RE.match(line)
            if m:
                key = m.group(1).strip().lower()
                meta[key] = m.group(2).strip()
                continue
            if line.strip() == "":
                in_header = False
                continue
            in_header = False
            body_lines.append(line)
        else:
            body_lines.append(line)

    sql_body = "\n".join(body_lines).strip()
    query_id = meta.get("id") or path.stem.split("_", 1)[0]
    return SqlEntry(
        id=query_id.upper(),
        title=meta.get("title") or path.stem,
        skills=meta.get("skills") or "",
        tables=meta.get("tables") or "",
        params=meta.get("params") or "none",
        level=meta.get("level") or default_level,
        path=path,
        sql=sql_body,
    )
