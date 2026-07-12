"""Data cleaning rules C-01 … C-10."""

from __future__ import annotations

import re
import unicodedata
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any

_EMPTY = {"", "none", "null", "nan", "nat", "n/a", "-"}


def strip_strings(row: dict[str, Any]) -> dict[str, Any]:
    """C-01: trim whitespace on all string values."""
    out: dict[str, Any] = {}
    for k, v in row.items():
        if isinstance(v, str):
            out[k] = v.strip()
        else:
            out[k] = v
    return out


def empty_to_none(row: dict[str, Any], fields: list[str] | None = None) -> dict[str, Any]:
    """C-02: empty string → None for optional fields (or all string fields)."""
    out = dict(row)
    keys = fields if fields is not None else list(out.keys())
    for k in keys:
        v = out.get(k)
        if v is None:
            continue
        if isinstance(v, str) and v.strip().lower() in _EMPTY:
            out[k] = None
    return out


def normalize_email(value: str | None) -> str | None:
    """C-03: lower-case email."""
    if value is None or value == "":
        return None
    return value.strip().lower()


def normalize_phone(value: str | None) -> str | None:
    """C-04: keep digits and leading +."""
    if value is None or value == "":
        return None
    s = value.strip()
    if s.startswith("+"):
        digits = re.sub(r"\D", "", s[1:])
        return f"+{digits}" if digits else None
    digits = re.sub(r"\D", "", s)
    return digits or None


def normalize_enum(value: str | None) -> str | None:
    """C-05: lower-case enums."""
    if value is None or value == "":
        return None
    return value.strip().lower().replace("-", "_").replace(" ", "_")


def parse_datetime(value: Any) -> datetime | date | None:
    """C-06: parse multi-format dates/datetimes."""
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    s = str(value).strip()
    if not s:
        return None
    # ISO first
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        pass
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d", "%m/%d/%Y"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    raise ValueError(f"Unrecognized date format: {value!r}")


def parse_decimal(value: Any) -> Decimal | None:
    if value is None or value == "":
        return None
    if isinstance(value, Decimal):
        return value
    s = str(value).strip().replace(",", "")
    if not s:
        return None
    try:
        return Decimal(s)
    except InvalidOperation as exc:
        raise ValueError(f"Invalid decimal: {value!r}") from exc


def parse_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        raise ValueError("boolean is not a valid int")
    if isinstance(value, int):
        return value
    s = str(value).strip()
    if not s:
        return None
    return int(float(s))


def parse_bool(value: Any) -> bool | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return value
    s = str(value).strip().lower()
    if s in {"1", "true", "t", "yes", "y"}:
        return True
    if s in {"0", "false", "f", "no", "n"}:
        return False
    raise ValueError(f"Invalid boolean: {value!r}")


def unicode_nfc(value: str | None) -> str | None:
    """C-09: Unicode NFC normalize."""
    if value is None:
        return None
    return unicodedata.normalize("NFC", value)


def dedupe_by_key(
    rows: list[dict[str, Any]],
    key: str,
    *,
    keep: str = "last",
) -> list[dict[str, Any]]:
    """C-07: deduplicate by natural key (keep last or first)."""
    if keep not in {"last", "first"}:
        raise ValueError("keep must be 'last' or 'first'")
    seen: dict[Any, dict[str, Any]] = {}
    order: list[Any] = []
    for row in rows:
        k = row.get(key)
        if k is None or k == "":
            # keep rows without key as unique by object id path
            order.append(id(row))
            seen[id(row)] = row
            continue
        if k not in seen:
            order.append(k)
        if keep == "last" or k not in seen:
            seen[k] = row
    # rebuild preserving first-seen order of keys
    result: list[dict[str, Any]] = []
    used: set[Any] = set()
    for k in order:
        if k in used:
            continue
        used.add(k)
        if k in seen:
            result.append(seen[k])
    return result


def clean_row_common(row: dict[str, Any]) -> dict[str, Any]:
    """Apply C-01, C-02, C-09 to a raw row."""
    row = strip_strings(row)
    row = empty_to_none(row)
    for k, v in list(row.items()):
        if isinstance(v, str):
            row[k] = unicode_nfc(v)
    return row
