# 7. Python Architecture

## 7.1 Nguyên tắc

1. **Separation of concerns** — I/O, domain, presentation tách bạch  
2. **Dependency rule** — dashboard/reports → services → repositories → models/db  
3. **Thin UI** — Streamlit chỉ layout + gọi service  
4. **Fat metrics definition, thin charts** — một nơi định nghĩa KPI  
5. **Type hints everywhere** — hỗ trợ mypy  
6. **Config centralized** — pydantic-settings  
7. **No framework web API** — CLI + Streamlit only  

---

## 7.2 Sơ đồ phụ thuộc

```text
cli / dashboard / reports entrypoints
            │
            ▼
        services  ◄── analytics, etl orchestration
            │
            ▼
      repositories
            │
            ▼
    models (SQLAlchemy) + database session
            │
            ▼
         PostgreSQL

schemas (Pydantic) dùng bởi etl + services validation
config dùng bởi tất cả
utils/logging dùng bởi tất cả
```

---

## 7.3 Package map

### `app/config`

**Nhiệm vụ:** cấu hình runtime.

| Thành phần | Mô tả |
|------------|--------|
| `settings.py` | `BaseSettings`: DATABASE_URL, LOG_LEVEL, ETL_BATCH_SIZE, DEFAULT_CURRENCY, DATA_DIR, REPORT_DIR |
| `.env` loading | python-dotenv via pydantic-settings |

**Không:** business logic.

---

### `app/database`

**Nhiệm vụ:** engine, session factory, connection helpers.

| Thành phần | Mô tả |
|------------|--------|
| `engine.py` | `create_engine` psycopg |
| `session.py` | `SessionLocal`, context manager `get_session()` |
| `base.py` | `DeclarativeBase` |

---

### `app/models`

**Nhiệm vụ:** SQLAlchemy 2.x mapped classes ≈ 16 tables + calendar.

| Thành phần | Mô tả |
|------------|--------|
| `mixins.py` | TimestampMixin, SoftDeleteMixin |
| `region.py`, `store.py`, … | one module per aggregate/table group |
| `__init__.py` | export metadata for Alembic |

**Không:** query phức tạp (để repository).

---

### `app/schemas`

**Nhiệm vụ:** Pydantic models cho ETL input, API-like DTOs nội bộ, report params.

| Ví dụ | |
|-------|--|
| `CustomerIn` / `CustomerOut` | |
| `OrderIn` | nested items optional |
| `ReportParams` | date range, filters |
| `KPIResult` | typed metrics |

---

### `app/repositories`

**Nhiệm vụ:** data access — CRUD đơn giản + query methods dùng SQLAlchemy select.

| Repo | Ví dụ methods |
|------|----------------|
| `OrderRepository` | `get_by_number`, `list_for_period` |
| `ProductRepository` | `upsert_by_sku`, `list_active` |
| `AnalyticsRepository` | raw SQL text cho reporting nặng (hoặc gọi file sql) |

**Quy tắc:** mọi filter `deleted_at IS NULL` mặc định cho master.

---

### `app/services`

**Nhiệm vụ:** business use-cases orchestration.

| Service | Nhiệm vụ |
|---------|----------|
| `metrics_service` | Revenue, Profit, AOV, counts — **single source of metric truth** |
| `customer_analytics_service` | RFM, CLV, repeat rate |
| `product_analytics_service` | ABC, top products, margin |
| `inventory_service` | low stock, velocity |
| `etl_service` | orchestrate extract→load |
| `report_service` | build report data packages |
| `seed_service` | generate & insert fake data |

Services gọi repositories + pandas khi cần; **không** import Streamlit.

---

### `app/etl`

**Nhiệm vụ:** pipeline chi tiết (xem `etl-design.md`).

```text
etl/
  extractors/
  validators/
  cleaning/
  transformers/
  loaders/
  pipeline.py
  manifest.py
```

---

### `app/analytics`

**Nhiệm vụ:** pure/analytical transforms trên DataFrame hoặc kết quả SQL.

| Module | |
|--------|--|
| `rfm.py` | score + segment |
| `abc.py` | cumulative classification |
| `cohort.py` | retention matrix |
| `trends.py` | MoM, rolling |
| `descriptive.py` | describe, histograms data |

Ưu tiên hàm pure để unit test dễ.

---

### `app/visualization`

**Nhiệm vụ:** tạo figure Plotly/Matplotlib từ DataFrame — **không** query DB.

| Module | |
|--------|--|
| `plotly_charts.py` | line, bar, pie, area, scatter, hist, heatmap, treemap |
| `matplotlib_charts.py` | static charts cho PDF |
| `styles.py` | color palette, template |

---

### `app/reports`

**Nhiệm vụ:** xuất Excel (openpyxl) và PDF (reportlab).

```text
reports/
  excel/
    workbook_builder.py
    sheets/
  pdf/
    pdf_builder.py
    components/
  templates/   # optional config for sections
  generators/
    daily.py
    weekly.py
    monthly.py
    quarterly.py
    yearly.py
```

---

### `app/dashboard`

**Nhiệm vụ:** Streamlit multipage app.

```text
dashboard/
  app.py              # entry
  pages/
    1_overview.py
    2_sales.py
    3_products.py
    4_customers.py
    5_inventory.py
  components/
    kpi_cards.py
    filters.py
    charts.py
  state.py            # session state helpers
```

---

### `app/utils`

| Module | |
|--------|--|
| `logging.py` | loguru configure |
| `dates.py` | date range helpers |
| `money.py` | format VND |
| `paths.py` | project root, data dirs |
| `errors.py` | exception hierarchy |

---

### `app/cli`

**Nhiệm vụ:** Typer entrypoint.

```text
Commands (design):
  db init | migrate | ping | reset
  seed run --scale 10k
  etl run | run-all
  report generate --type monthly --format excel|pdf|both
  sql list | run --id R04
  dashboard   # launches streamlit (subprocess or docs)
```

Package install: `pyproject.toml` script `sales-dashboard = app.cli:app`.

---

### `tests`

Xem `testing-plan.md`. Mirror package structure:

```text
tests/
  unit/
  integration/
  data_quality/
  conftest.py
```

---

### `alembic`

Migration environment; `env.py` import metadata từ `app.models`.

---

### `sql/`

SQL learning catalog (không nhất thiết import Python; runner optional).

---

## 7.4 Cross-cutting patterns

### Session management

```text
with get_session() as session:
    repo = OrderRepository(session)
    service.do(repo)
    session.commit()
```

CLI/dashboard mỗi request/command một session scope rõ.

### Error hierarchy

```text
AppError
  ConfigError
  DatabaseError
  ValidationError
  ETLError
  ReportError
  NotFoundError
```

### Metrics single source

Mọi KPI card, Excel summary, PDF cover gọi `MetricsService.summary(filters)` — tránh lệch số.

### Filtering DTO

```text
class AnalyticsFilter:
  start_date, end_date
  store_ids, region_ids
  category_ids, employee_ids
  customer_id optional
  order_statuses default paid+completed
```

---

## 7.5 Library usage map

| Library | Where |
|---------|-------|
| SQLAlchemy 2.x | models, repositories |
| psycopg | driver via SQLAlchemy |
| Alembic | migrations |
| pandas/numpy | analytics, etl extract, some reports |
| Plotly | Streamlit interactive |
| Matplotlib | PDF static images |
| openpyxl | Excel |
| reportlab | PDF layout |
| pydantic | schemas |
| pydantic-settings | config |
| loguru | logging |
| Typer | CLI |
| Faker | seed |
| pytest | tests |
| Streamlit | dashboard only |

---

## 7.6 What NOT to put where

| Anti-pattern | Thay bằng |
|--------------|-----------|
| SQL string trong Streamlit page | service/repository |
| Business rule trong repository | service |
| pandas.read_csv trong dashboard | ETL rồi query DB |
| Duplicate revenue formula | MetricsService |
| Bare `print` | loguru |

---

## 7.7 Checklist kiến trúc

- [ ] Packages đúng ranh giới  
- [ ] Metrics tập trung  
- [ ] ETL tách extract/validate/clean/transform/load  
- [ ] Dashboard mỏng  
- [ ] CLI đủ seed/etl/report/db  
- [ ] Tests mirror structure  
