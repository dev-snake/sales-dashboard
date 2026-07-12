# 13. Testing Plan

## 13.1 Mục tiêu

Đảm bảo:

1. Hàm pure (cleaning, metrics math, RFM bins) đúng  
2. DB constraints + repository behavior đúng  
3. ETL reject/load đúng  
4. Metric consistency (SQL vs service) trên fixture nhỏ  
5. Không cần full 1M data trong CI local  

Framework: **pytest**  
Optional: `pytest-cov`  

---

## 13.2 Kim tự tháp kiểm thử

```text
        ┌──────────────┐
        │  Manual E2E  │  Streamlit click, report open
        │  (light)     │
        ├──────────────┤
        │ Integration  │  PostgreSQL test DB, ETL file→DB
        ├──────────────┤
        │ Data Quality │  constraints, reconciliations
        ├──────────────┤
        │ Unit tests   │  majority
        └──────────────┘
```

---

## 13.3 Unit Tests

### Phạm vi

| Module | Ví dụ test cases |
|--------|------------------|
| `etl/cleaning` | trim, empty→None, email lower, phone digits, date multi-format |
| `analytics/rfm` | score boundaries, segment labels |
| `analytics/abc` | cumulative 80/95 cut |
| `analytics/cohort` | pivot shape |
| `analytics/trends` | MoM pct with zero guard |
| `services/metrics` | pure calc from sample frames if extracted |
| `utils/money` | format |
| `utils/dates` | period bounds daily/weekly/monthly |
| `schemas` | pydantic accept/reject rows |
| `visualization` | create_bar returns figure with expected trace count (smoke) |

### Đặc điểm

- Không cần PostgreSQL  
- Nhanh, deterministic (`seed=42`)  
- Fixtures inline list[dict] / small DataFrame  

### Naming

```text
tests/unit/analytics/test_rfm.py
tests/unit/etl/test_cleaning.py
```

---

## 13.4 Integration Tests

### Yêu cầu môi trường

- PostgreSQL test database: `sales_dashboard_test`  
- URL từ env `TEST_DATABASE_URL`  
- `conftest.py`: create schema via Alembic upgrade, truncate between tests hoặc transaction rollback pattern  

### Phạm vi

| Area | Cases |
|------|-------|
| Models/Migration | tables exist, FK works |
| Repositories | insert customer, get by code, soft delete filters |
| Seed XS | seed 100 scale completes, order FKs valid |
| ETL CSV | valid file loads N rows; invalid produces reject |
| MetricsService | after fixture orders, revenue matches hand-calc |
| Report excel | monthly generator creates file with expected sheets |
| CLI smoke | `db ping` exit 0 (optional typer testing) |

### Isolation

- Prefer **function-scoped** truncate of transactional tables  
- Or nested transaction rollback if using SQLAlchemy connection  

---

## 13.5 Data Validation Tests

Kiểm tra **chất lượng / bất biến nghiệp vụ** trên DB sau seed hoặc fixture.

| ID | Assertion |
|----|-----------|
| DQ01 | No orphan order_items |
| DQ02 | No order with store employee mismatch (employee.store_id == order.store_id) — nếu enforce |
| DQ03 | line_total ≈ qty*price - discount (tolerance 0.01) |
| DQ04 | SUM(payments completed) ≤ order.total + tolerance OR policy multi-pay |
| DQ05 | return.quantity ≤ order_item.quantity |
| DQ06 | inventory.quantity_on_hand ≥ 0 |
| DQ07 | unique natural keys no duplicates |
| DQ08 | revenue query only paid/completed |
| DQ09 | calendar covers min/max order_date |
| DQ10 | deleted masters not referenced by new seed (if any) |

Chạy như `tests/data_quality/test_invariants.py` trên scale XS.

---

## 13.6 SQL catalog tests (P1)

Không assert 135 queries đầy đủ.

- Smoke: parse/execute subset `B01, I01, A09, R01, R23` trên seed XS  
- Result columns non-empty where expected  

---

## 13.7 What we don't automate heavily

- Full Streamlit UI pixel tests  
- 1M seed duration  
- Plotly visual regression  

Manual checklist trong roadmap phase 8–9.

---

## 13.8 Fixtures design

```text
tests/conftest.py
  - settings override
  - engine/session for test DB
  - sample_products
  - sample_orders_bundle (customer, store, employee, order, 2 items, payment)

tests/fixtures/files/
  - customers_valid.csv
  - customers_invalid.csv
```

---

## 13.9 Coverage targets

| Package | Target |
|---------|--------|
| `app/etl/cleaning` + validators | ≥ 85% |
| `app/analytics` | ≥ 80% |
| `app/services/metrics_service` | ≥ 80% |
| repositories | ≥ 60% |
| dashboard | smoke optional |
| Overall core | ≥ 70% |

---

## 13.10 Quality gates (local, no CI/CD)

Developer chạy trước khi kết thúc phase:

```text
ruff check .
black --check .
mypy app
pytest -q
```

(CI/CD intentionally out of scope — document as manual discipline.)

---

## 13.11 Test data vs seed

| | Unit | Integration | Demo |
|--|------|-------------|------|
| Size | tiny | XS seed or micro fixture | M/L |
| Speed | ms | seconds–minute | minutes |
| DB | no | yes | yes |

---

## 13.12 Checklist Testing phase

- [x] conftest + TEST_DATABASE_URL documented (README + `.env.example`)  
- [x] unit suite green (default `pytest -m "not integration and not data_quality"`)  
- [x] integration tests (schema, ETL fixtures, metrics hand-calc) — skip if no DB  
- [x] ETL valid/invalid fixture files under `tests/fixtures/files/`  
- [x] data quality invariants DQ01/03/05–09 (skip if empty tables)  
- [x] ruff/black/mypy + `scripts/quality.sh`  
- [x] README section “How to test”  
