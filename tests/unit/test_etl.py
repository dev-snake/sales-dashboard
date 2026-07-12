"""Unit tests for ETL cleaning, extractors, validation (no DB)."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from app.etl.cleaning.rules import (
    clean_row_common,
    dedupe_by_key,
    normalize_email,
    normalize_phone,
    parse_datetime,
    parse_decimal,
)
from app.etl.extractors.factory import get_extractor, get_extractor as ge
from app.etl.manifest import default_samples_manifest, load_manifest
from app.etl.validators.row_validator import validate_rows
from app.schemas.customer import CustomerIn
from app.schemas.order import OrderItemIn
from app.schemas.payment import PaymentIn
from app.schemas.product import ProductIn
from app.utils.errors import ETLError


def test_normalize_email_phone() -> None:
    assert normalize_email("  Foo@Example.COM ") == "foo@example.com"
    assert normalize_phone("+84 90-123-4567") == "+84901234567"
    assert normalize_phone("0901 234 567") == "0901234567"


def test_parse_datetime_formats() -> None:
    assert parse_datetime("2024-01-15") is not None
    assert parse_datetime("15/01/2024") is not None
    assert parse_datetime("2024-01-15T10:30:00+00:00") is not None


def test_parse_decimal() -> None:
    assert parse_decimal("1,250.50") == Decimal("1250.50")
    assert parse_decimal(None) is None


def test_clean_and_dedupe() -> None:
    rows = [
        clean_row_common({"code": " A ", "name": "x"}),
        clean_row_common({"code": "A", "name": "y"}),
        clean_row_common({"code": "", "name": "z"}),
    ]
    assert rows[0]["code"] == "A"
    deduped = dedupe_by_key(
        [{"code": "A", "v": 1}, {"code": "A", "v": 2}, {"code": "B", "v": 3}],
        "code",
        keep="last",
    )
    assert len(deduped) == 2
    assert next(r for r in deduped if r["code"] == "A")["v"] == 2


def test_validate_customers() -> None:
    valid, rejected = validate_rows(
        [
            {
                "code": "C1",
                "first_name": "Ann",
                "last_name": "Bee",
                "email": "Ann@X.COM",
            },
            {"code": "", "first_name": "X", "last_name": "Y"},
        ],
        CustomerIn,
    )
    assert len(valid) == 1
    assert valid[0].email == "ann@x.com"
    assert len(rejected) == 1
    assert "_errors" in rejected[0]


def test_validate_product_and_item() -> None:
    products, _ = validate_rows(
        [
            {
                "sku": "S1",
                "name": "P",
                "category_code": "CAT",
                "unit_price": "1000",
                "cost_price": "500",
            }
        ],
        ProductIn,
    )
    assert products[0].unit_price == Decimal("1000")

    items, bad = validate_rows(
        [
            {
                "order_number": "O1",
                "product_sku": "S1",
                "quantity": "2",
                "unit_price": "10",
                "unit_cost": "5",
                "discount_amount": "0",
            },
            {
                "order_number": "O1",
                "product_sku": "S1",
                "quantity": "0",
                "unit_price": "10",
                "unit_cost": "5",
            },
        ],
        OrderItemIn,
    )
    assert len(items) == 1
    assert len(bad) == 1


def test_validate_payment() -> None:
    ok, bad = validate_rows(
        [
            {
                "payment_number": "P1",
                "order_number": "O1",
                "method": "Cash",
                "amount": "100",
                "status": "COMPLETED",
            }
        ],
        PaymentIn,
    )
    assert ok[0].method == "cash"
    assert not bad


def test_extractors_on_samples() -> None:
    root = Path(__file__).resolve().parents[2]
    samples = root / "datasets" / "raw" / "samples"
    if not (samples / "customers.csv").is_file():
        pytest.skip("sample files missing")

    csv_df = get_extractor(samples / "customers.csv").extract(samples / "customers.csv")
    assert len(csv_df) == 50
    assert "code" in csv_df.columns

    xlsx = get_extractor(samples / "products.xlsx").extract(samples / "products.xlsx")
    assert len(xlsx) == 30

    js = get_extractor(samples / "payments.json").extract(samples / "payments.json")
    assert len(js) == 20


def test_unsupported_extension() -> None:
    with pytest.raises(ETLError):
        ge(Path("file.parquet"))


def test_default_samples_manifest() -> None:
    mf = default_samples_manifest()
    assert mf.ensure_sample_masters is True
    assert [j.entity for j in mf.jobs] == [
        "customers",
        "products",
        "orders",
        "order_items",
        "payments",
    ]


def test_load_manifest_example() -> None:
    root = Path(__file__).resolve().parents[2]
    path = root / "datasets" / "manifest.example.yaml"
    mf = load_manifest(path)
    assert mf.ensure_sample_masters is True
    assert len(mf.jobs) == 5
    assert mf.jobs[0].entity == "customers"
