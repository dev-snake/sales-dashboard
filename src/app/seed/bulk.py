"""Bulk insert helpers for seed performance."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import Any

from loguru import logger
from sqlalchemy import insert
from sqlalchemy.orm import Session


def chunked[T](items: Sequence[T], size: int) -> Iterable[Sequence[T]]:
    for i in range(0, len(items), size):
        yield items[i : i + size]


def bulk_insert(
    session: Session,
    model: type[Any],
    rows: Sequence[dict[str, Any]],
    *,
    batch_size: int = 2000,
    returning_id: bool = False,
) -> list[int]:
    """Insert rows in batches. Optionally return generated ``id`` values."""
    if not rows:
        return []

    ids: list[int] = []
    table = model.__table__
    total = len(rows)

    for i, batch in enumerate(chunked(list(rows), batch_size), start=1):
        stmt = insert(table)
        if returning_id and "id" in table.c:
            result = session.execute(stmt.returning(table.c.id), list(batch))
            ids.extend(result.scalars().all())
        else:
            session.execute(stmt, list(batch))
        if i % 10 == 0 or i * batch_size >= total:
            logger.info(
                "Bulk insert {} | batch {} | rows {}/{}",
                table.name,
                i,
                min(i * batch_size, total),
                total,
            )

    session.flush()
    return ids
