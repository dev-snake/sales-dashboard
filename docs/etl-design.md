# 6. ETL / ELT Design

## 6.1 Tổng quan

Hệ thống dùng pipeline **ETL** (transform trước/trong lúc load) phù hợp file batch và PostgreSQL local:

```text
  Sources (CSV / Excel / JSON)
            │
            ▼
     ┌──────────────┐
     │   EXTRACT    │  đọc file, normalize thành records
     └──────┬───────┘
            ▼
     ┌──────────────┐
     │  VALIDATION  │  Pydantic schema + type coercion
     └──────┬───────┘
            ▼
     ┌──────────────┐
     │   CLEANING   │  trim, null policy, dedupe, standardize
     └──────┬───────┘
            ▼
     ┌──────────────┐
     │ TRANSFORMATION  │  map columns, derive fields, FK resolve
     └──────┬───────┘
            ▼
     ┌──────────────┐
     │     LOAD     │  insert/upsert PostgreSQL (batched)
     └──────┬───────┘
            ▼
     SQL Analytics → Python Analytics → Visualization → Dashboard → Export
```

**ELT elements:** một số analytic transform (RFM, ABC) thực hiện **sau load** bằng SQL/Python trên PostgreSQL → hybrid.

---

## 6.2 Nguồn dữ liệu

| Format | Use case | Thư mục gợi ý |
|--------|----------|---------------|
| CSV | Export POS/ERP, bulk seed intermediate | `data/raw/csv/` |
| Excel | Báo cáo thủ công từ store manager | `data/raw/excel/` |
| JSON | API dump mô phỏng / nested catalogs | `data/raw/json/` |

### Entity files dự kiến (ví dụ)

| Entity | File mẫu |
|--------|----------|
| customers | `customers.csv` |
| products | `products.xlsx` |
| orders | `orders_2024.csv` |
| order_items | `order_items_2024.csv` |
| payments | `payments.json` |
| inventory | `inventory_snapshot.csv` |

**Staging cleaned:** `data/staging/`  
**Rejected:** `data/rejected/YYYYMMDD_HHMMSS_<entity>.csv`  
**Processed archive (optional):** `data/archive/`

---

## 6.3 Chi tiết từng bước

### 6.3.1 Extract

**Nhiệm vụ**

- Phát hiện format theo extension
- Đọc với encoding UTF-8 (fallback latin-1 có log warning)
- Excel: sheet name config hoặc first sheet
- JSON: list of objects hoặc `{ "records": [...] }`
- Trả về `Iterable[dict[str, Any]]` hoặc pandas DataFrame (chốt: **DataFrame ở boundary extract**, convert row model sau)

** thrách nhiệm module:** `app/etl/extractors/`

| Class/Module | Responsibility |
|--------------|----------------|
| `CsvExtractor` | pandas.read_csv / csv module |
| `ExcelExtractor` | openpyxl/pandas.read_excel |
| `JsonExtractor` | json.load + normalize |

**Logging:** path, size, row count, duration.

---

### 6.3.2 Validation

**Nhiệm vụ**

- Map mỗi row → Pydantic model (`CustomerIn`, `OrderIn`, …)
- Coerce types (string dates → datetime)
- Required fields, ranges, enum sets
- Tách `valid_rows` / `invalid_rows` kèm error messages

**Không** validate FK ở bước này nếu master chưa load — FK check ở **Load** hoặc **Transform resolve** phase.

**Module:** `app/etl/validators/` + `app/schemas/` (Pydantic)

**Output artifact:** reject file với cột `_errors`

---

### 6.3.3 Cleaning

**Quy tắc làm sạch (catalog)**

| Rule ID | Mô tả | Áp dụng |
|---------|-------|---------|
| C-01 | Strip whitespace string fields | all |
| C-02 | Empty string → NULL | optional fields |
| C-03 | Normalize email lower-case | customers, employees |
| C-04 | Phone: giữ digits và leading + | customers |
| C-05 | Standardize status enums lower-case | orders, payments |
| C-06 | Parse dates multi-format | `%Y-%m-%d`, `%d/%m/%Y`, ISO |
| C-07 | Deduplicate by natural key keep last | all masters |
| C-08 | Cap extreme outliers flag (không auto-drop money) | optional warn |
| C-09 | Unicode normalize NFC | names |
| C-10 | Default country/currency if missing | config |

**Module:** `app/etl/cleaning/`

---

### 6.3.4 Transformation

**Nhiệm vụ**

- Rename columns source → canonical
- Derive: `full_name`, `line_total`, `date_id`
- Map business codes → surrogate IDs (lookup DB)
- Split/merge columns
- Attach default `store_id` nếu file thiếu (config)
- Order header totals recompute từ lines (optional mode)

**Module:** `app/etl/transformers/`

**Thứ tự transform phụ thuộc FK (load order):**

```text
1. regions
2. stores
3. employees
4. suppliers, brands, categories
5. products
6. customers
7. promotions
8. calendar (generated, not from file usually)
9. orders
10. order_items
11. payments
12. inventory
13. stock_movements
14. returns
```

---

### 6.3.5 Load

**Chiến lược**

| Entity type | Strategy |
|-------------|----------|
| Master (code unique) | UPSERT on natural key (`ON CONFLICT DO UPDATE`) |
| Orders / items | Insert; fail on duplicate order_number (or upsert header) |
| Calendar | Generate once; skip if exists |
| Inventory | UPSERT (store_id, product_id) |

**Batch size:** config `ETL_BATCH_SIZE` default 1000  
**Transaction:** per batch  
**Driver:** SQLAlchemy 2.x + psycopg  

**Module:** `app/etl/loaders/` + repositories

**Post-load hooks (optional):**

- Recompute inventory from movements (validation mode)
- Refresh reporting views if any

---

### 6.3.6 SQL Analytics (post-load)

Chạy catalog reporting queries; không sửa raw tables.  
Có thể materialize kết quả RFM vào bảng optional `analytics_rfm` (P2).

---

### 6.3.7 Python Analytics

Đọc từ DB (SQLAlchemy/pandas.read_sql) → RFM segment labels, cohort pivot, ABC cutoffs tinh chỉnh → trả DataFrame cho viz/report.

---

### 6.3.8 Visualization & Dashboard & Export

Xem `dashboard-design.md`, `data-visualization.md`, `reporting-design.md`.  
ETL chỉ **cung cấp data đúng**; presentation tách layer.

---

## 6.4 Pipeline orchestration (không Airflow)

**CLI Typer commands (thiết kế):**

```text
etl extract   --source ...
etl validate  --entity customers --file ...
etl run       --entity customers --file ...     # full pipeline one entity
etl run-all   --manifest data/manifest.yaml     # ordered multi-entity
etl status    # last run summary from logs/table
```

**Manifest ý tưởng:**

```yaml
# data/manifest.example.yaml  (implement later)
jobs:
  - entity: regions
    path: data/raw/csv/regions.csv
  - entity: stores
    path: data/raw/csv/stores.csv
  # ...
```

Single process, sequential — đủ cho portfolio.

---

## 6.5 Run metadata (optional table)

Bảng optional `etl_runs` / `etl_run_items` (P1):

| Column | Meaning |
|--------|---------|
| run_id | UUID |
| entity | customers |
| source_path | |
| rows_read / valid / rejected / loaded | |
| started_at / finished_at | |
| status | success/failed/partial |
| error_message | |

Phục vụ reliability & demo logging.

---

## 6.6 Error handling trong ETL

```text
File not found → ETLError, exit 2
Schema mismatch → reject all or column mapper fail fast
Row invalid → reject row, continue (default)
Batch DB error → rollback batch, log, fail job or continue next file (config)
```

**Modes:**

- `strict`: any reject → fail job  
- `lenient` (default): load valid, write rejects  

---

## 6.7 Idempotency

| Approach | Khi dùng |
|----------|----------|
| Upsert natural keys | Re-run master safe |
| Delete-by-source + reload | Dev seed |
| Truncate all + seed | Demo reset CLI `db reset --yes` |

Document rõ trong CLI help để tránh xóa nhầm production-like data.

---

## 6.8 Data contracts (ví dụ customers CSV)

| Column | Type | Required | Notes |
|--------|------|----------|-------|
| code | str | yes | unique |
| first_name | str | yes | |
| last_name | str | yes | |
| email | str | no | unique if present |
| phone | str | no | |
| city | str | no | |
| region_code | str | no | resolve → region_id |
| registered_at | datetime | no | default now |

Tương tự contracts cho mọi entity — implement trong `docs/data-contracts/` hoặc `app/schemas` khi code (Phase 5).

---

## 6.9 ELT vs ETL decision log

| Transform | Where | Why |
|-----------|-------|-----|
| Clean phone/email | ETL pre-load | Dirty data không vào DB |
| Resolve region_code | ETL | FK integrity |
| line_total | ETL + CHECK app | Consistency |
| RFM scores | SQL/Python post | Cần full history |
| Cohort matrix | Python post | Pivot convenience |
| KPI for dashboard | SQL views/queries | Performance |

---

## 6.10 Testing ETL

- Unit: cleaning functions, date parse, phone normalize  
- Integration: temp CSV → test DB → row counts  
- Validation: invalid row appears in reject file  

Xem `testing-plan.md`.

---

## 6.11 Checklist ETL phase

- [x] Extractors CSV/Excel/JSON  
- [x] Pydantic schemas per entity  
- [x] Cleaning rules C-01…C-10 (core implemented)  
- [x] Load order FK-safe (manifest / samples)  
- [x] Upsert by natural key (customers/products/orders/payments)  
- [x] Reject files + loguru metrics  
- [x] CLI `etl run` / `etl run-all`  
- [x] Sample raw files in `datasets/raw/samples/`  
- [x] Docs data contracts (`docs/data-contracts.md`)  
- [ ] Live PG verification (`etl run-all --samples`) — needs DATABASE_URL  

