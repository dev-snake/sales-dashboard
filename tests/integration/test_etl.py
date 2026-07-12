"""Integration: ETL load from fixture files."""

from __future__ import annotations

from pathlib import Path

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.etl.pipeline import EtlPipeline
from app.etl.transformers.lookups import ensure_sample_masters
from app.models import Customer

pytestmark = pytest.mark.integration


def test_etl_customers_valid_and_invalid(
    db_session: Session,
    fixtures_dir: Path,
) -> None:
    ensure_sample_masters(db_session)
    pipeline = EtlPipeline(db_session, strict=False, ensure_masters=False)

    valid_path = fixtures_dir / "customers_valid.csv"
    invalid_path = fixtures_dir / "customers_invalid.csv"
    assert valid_path.is_file()

    result_ok = pipeline.run("customers", valid_path)
    assert result_ok.rows_loaded >= 2
    assert result_ok.status in {"success", "partial"}

    # loaded codes present
    codes = set(
        db_session.scalars(select(Customer.code).where(Customer.code.like("CUS-TEST-%"))).all()
    )
    assert "CUS-TEST-001" in codes

    result_bad = pipeline.run("customers", invalid_path)
    assert result_bad.rows_rejected >= 1
    assert result_bad.reject_path is not None or result_bad.rows_rejected > 0
