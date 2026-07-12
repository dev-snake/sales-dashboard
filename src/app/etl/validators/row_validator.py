"""Validate cleaned rows against Pydantic schemas."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ValidationError


def validate_rows[T: BaseModel](
    rows: list[dict[str, Any]],
    model: type[T],
) -> tuple[list[T], list[dict[str, Any]]]:
    """Split into valid models and reject dicts with ``_errors``."""
    valid: list[T] = []
    rejected: list[dict[str, Any]] = []
    for row in rows:
        try:
            valid.append(model.model_validate(row))
        except ValidationError as exc:
            bad = dict(row)
            bad["_errors"] = "; ".join(
                f"{'.'.join(str(x) for x in e.get('loc', ()))}: {e.get('msg')}"
                for e in exc.errors()
            )
            rejected.append(bad)
    return valid, rejected
