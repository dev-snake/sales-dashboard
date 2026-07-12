"""ETL pipeline: extract → clean → validate → transform → load."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from loguru import logger
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import get_settings
from app.etl.cleaning.rules import clean_row_common, dedupe_by_key
from app.etl.extractors.base import dataframe_to_records
from app.etl.extractors.factory import get_extractor
from app.etl.loaders.upsert import load_entity
from app.etl.reject import write_rejects
from app.etl.result import EtlResult
from app.etl.transformers.entities import (
    require_supported_entity,
    transform_customers,
    transform_order_items,
    transform_orders,
    transform_payments,
    transform_products,
)
from app.etl.transformers.lookups import LookupCache, ensure_sample_masters
from app.etl.validators.row_validator import validate_rows
from app.schemas.customer import CustomerIn
from app.schemas.order import OrderIn, OrderItemIn
from app.schemas.payment import PaymentIn
from app.schemas.product import ProductIn
from app.utils.errors import ETLError

_ENTITY_MODEL: dict[str, type[BaseModel]] = {
    "customers": CustomerIn,
    "products": ProductIn,
    "orders": OrderIn,
    "order_items": OrderItemIn,
    "payments": PaymentIn,
}

_DEDUPE_KEY: dict[str, str] = {
    "customers": "code",
    "products": "sku",
    "orders": "order_number",
    "payments": "payment_number",
}


class EtlPipeline:
    """Run full ETL for a single entity file."""

    def __init__(
        self,
        session: Session,
        *,
        strict: bool | None = None,
        ensure_masters: bool = False,
    ) -> None:
        self.session = session
        self.settings = get_settings()
        self.strict = self.settings.etl_strict_mode if strict is None else strict
        self.ensure_masters = ensure_masters
        self.batch_size = self.settings.etl_batch_size

    def run(self, entity: str, path: Path) -> EtlResult:
        entity = require_supported_entity(entity)
        path = Path(path)
        if not path.is_file():
            raise ETLError(f"Source file not found: {path}")

        started = time.perf_counter()
        result = EtlResult(entity=entity, source_path=path)

        if self.ensure_masters:
            ensure_sample_masters(self.session)

        # 1) Extract
        extractor = get_extractor(path)
        df = extractor.extract(path)
        raw_rows = dataframe_to_records(df)
        result.rows_read = len(raw_rows)
        logger.info("ETL extract done | entity={} rows={}", entity, result.rows_read)

        # 2) Clean
        cleaned = [clean_row_common(r) for r in raw_rows]
        key = _DEDUPE_KEY.get(entity)
        if key:
            cleaned = dedupe_by_key(cleaned, key, keep="last")

        # 3) Validate
        model = _ENTITY_MODEL[entity]
        valid_models, rejected = validate_rows(cleaned, model)
        result.rows_valid = len(valid_models)
        result.rows_rejected = len(rejected)

        if self.strict and rejected:
            result.reject_path = write_rejects(entity, rejected)
            result.errors.append(f"strict mode: {len(rejected)} invalid rows (see reject file)")
            result.duration_seconds = time.perf_counter() - started
            return result

        # 4) Transform (FK resolve)
        lookups = LookupCache(self.session)
        ready, xf_rejected = self._transform(entity, valid_models, lookups)
        if xf_rejected:
            rejected.extend(xf_rejected)
            result.rows_rejected = len(rejected)
            result.rows_valid = result.rows_read - result.rows_rejected

        if self.strict and xf_rejected:
            result.reject_path = write_rejects(entity, rejected)
            result.errors.append(f"strict mode: {len(xf_rejected)} transform/FK failures")
            result.duration_seconds = time.perf_counter() - started
            return result

        # 5) Load
        try:
            loaded = load_entity(self.session, entity, ready, self.batch_size)
            self.session.commit()
            result.rows_loaded = loaded
        except Exception as exc:
            self.session.rollback()
            logger.exception("ETL load failed | entity={}", entity)
            result.errors.append(str(exc))
            result.reject_path = write_rejects(entity, rejected)
            result.duration_seconds = time.perf_counter() - started
            raise ETLError(f"Load failed for {entity}: {exc}") from exc

        result.reject_path = write_rejects(entity, rejected)
        result.duration_seconds = time.perf_counter() - started
        logger.info(
            "ETL complete | entity={} read={} valid={} rejected={} loaded={} duration={:.2f}s",
            entity,
            result.rows_read,
            result.rows_valid,
            result.rows_rejected,
            result.rows_loaded,
            result.duration_seconds,
        )
        return result

    def _transform(
        self,
        entity: str,
        models: list[Any],
        lookups: LookupCache,
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        if entity == "customers":
            return transform_customers(models, lookups)
        if entity == "products":
            return transform_products(models, lookups)
        if entity == "orders":
            return transform_orders(models, lookups)
        if entity == "order_items":
            # orders must already be loaded
            lookups.refresh()
            return transform_order_items(models, lookups)
        if entity == "payments":
            lookups.refresh()
            return transform_payments(models, lookups)
        raise ETLError(f"No transformer for {entity}")
