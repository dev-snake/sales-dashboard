# 14. Development Roadmap

Dự án chia **10 phases**. Mỗi phase độc lập đủ để review/portfolio.  
**Không nhảy phase** khi phase trước chưa đạt checklist (trừ khi user chỉ định).

> **Trạng thái hiện tại:** Phase 1 (Business Analysis) & phần lớn thiết kế (Phase 2 docs) **đã hoàn thành dưới dạng tài liệu**. Code bắt đầu khi user yêu cầu từng phase.

---

## Phase 1 — Business Analysis

### Mục tiêu

Chốt bài toán, persona, scope, FR/NFR.

### Công việc

1. Viết business requirements  
2. Viết functional requirements  
3. Viết non-functional requirements  
4. Glossary & success criteria  

### Deliverables

- [x] `docs/business-requirements.md`  
- [x] `docs/functional-requirements.md`  
- [x] `docs/non-functional-requirements.md`  
- [x] `docs/README.md` index  

### Checklist hoàn thành

- [x] Personas rõ  
- [x] In/out scope rõ  
- [x] FR có ID + priority  
- [x] NFR đo được trong ngữ cảnh portfolio  

### Ưu tiên

**P0 — foundation.** Phải xong trước mọi code.

---

## Phase 2 — Database Design

### Mục tiêu

Schema 3NF đầy đủ, ERD, quy ước constraint/index; (khi code) Alembic migrations.

### Công việc — Design (done)

1. Thiết kế 16 bảng + calendar  
2. PK/FK/index/CHECK/UNIQUE  
3. ERD  
4. Migration order  

### Công việc — Implementation (khi user yêu cầu)

1. Khởi tạo project `pyproject.toml`, package `app`  
2. SQLAlchemy models  
3. Alembic initial migration  
4. Trigger `updated_at`  
5. `db ping` / migrate CLI  

### Deliverables

- [x] `docs/database-design.md`  
- [x] `src/app/models/*` (16 tables + calendar, mixins)  
- [x] `alembic/versions/20260712_0001_initial_schema.py`  
- [x] CLI: `db migrate` / `db current` / `db downgrade` / `db tables`  
- [x] `docs/erd.mmd`  

### Checklist hoàn thành (implementation)

- [x] Models + constraints + indexes theo design  
- [x] Soft delete mixin trên master tables  
- [x] Trigger `set_updated_at` trong migration  
- [x] Unit tests metadata (18 tests)  
- [ ] `alembic upgrade head` / `sales-dashboard db migrate` trên PG local (cần `DATABASE_URL` hợp lệ)  
- [x] Documented DATABASE_URL setup (`database/README.md`, root README)  

### Ưu tiên

**P0**

---

## Phase 3 — Seed Data

### Mục tiêu

Sinh dữ liệu đa scale, realistic, deterministic.

### Công việc

1. `scale_config` counts  
2. Generators theo FK order  
3. Bulk insert strategy  
4. CLI `seed run --scale`  
5. Export samples nhỏ cho ETL  
6. Calendar generator  

### Deliverables

- [x] `docs/seed-data-design.md`  
- [x] `src/app/seed/*` + `SeedService`  
- [x] CLI `seed run` / `seed samples`  
- [x] `datasets/raw/samples/*` (customers CSV, products Excel, orders, payments JSON)  

### Checklist

- [x] Scale config 100 / 1k / 10k / 100k / 1m  
- [x] Calendar 2020–2030, masters, orders/items/payments/returns/inventory/movements  
- [x] Deterministic `--seed`  
- [x] Unit tests generators + sample export  
- [ ] `seed run --scale 100` trên PG local (cần DATABASE_URL hợp lệ)  
- [ ] Invariants DQ01–DQ10 (Phase Testing)  

### Ưu tiên

**P0** (cần data để SQL/ETL/Dashboard)

---

## Phase 4 — SQL Catalog

### Mục tiêu

≥ 100 (target 135) bài SQL + metric chuẩn.

### Công việc

1. Tạo `sql/` structure  
2. Basic 25  
3. Intermediate 30  
4. Advanced 35  
5. Reporting 30  
6. Optimization 15 + notes  
7. Catalog README  
8. Optional SQL runner CLI  

### Deliverables

- [x] `docs/sql-roadmap.md`  
- [x] `sql/**/*.sql` — **135** files (B25+I30+A35+R30+O15)  
- [x] `sql/README.md` catalog index  
- [x] `sql/metrics.md` metric definitions  
- [x] `sql/optimization/notes.md`  
- [x] CLI `sql list` / `show` / `run`  
- [x] `src/app/sql_catalog/` loader  

### Checklist

- [x] ≥ 100 queries (135)  
- [x] Metric definitions thống nhất  
- [x] Optimization lab notes  
- [x] Unit tests catalog (count, headers, R0x status filter)  
- [ ] `sql run` on live PG after seed (manual)  

### Ưu tiên

**P0 — learning core**

---

## Phase 5 — ETL / ELT

### Mục tiêu

Pipeline CSV/Excel/JSON → validate → clean → transform → load.

### Công việc

1. Extractors 3 formats  
2. Pydantic schemas  
3. Cleaning rules  
4. Transformers + FK resolve  
5. Loaders upsert  
6. Reject files + logging  
7. CLI `etl run` / `run-all`  
8. Sample manifest  

### Deliverables

- [x] `docs/etl-design.md`  
- [x] `src/app/etl/**` pipeline  
- [x] `src/app/schemas/*` inbound contracts  
- [x] `src/app/services/etl_service.py`  
- [x] CLI `etl run` / `etl run-all`  
- [x] `datasets/raw/samples/*` + `manifest.example.yaml`  
- [x] `docs/data-contracts.md`  

### Checklist

- [x] Extractors CSV/Excel/JSON  
- [x] Validate + clean + transform + upsert load  
- [x] Reject file under `datasets/rejected/`  
- [x] Unit tests cleaning/extract/validate/manifest  
- [ ] Live PG: `etl run-all --samples` (manual)  

### Ưu tiên

**P0**

---

## Phase 6 — Python Analytics

### Mục tiêu

pandas/numpy analytics + MetricsService thống nhất.

### Công việc

1. `MetricsService` (revenue, profit, margin, aov, counts)  
2. RFM  
3. ABC / Pareto  
4. Cohort  
5. Trends MoM  
6. Customer/Product analytics services  
7. Unit tests analytics  

### Deliverables

- [x] `docs/python-architecture.md`  
- [x] `src/app/analytics/*` — RFM, ABC, cohort, trends, descriptive  
- [x] `src/app/repositories/analytics.py`  
- [x] `MetricsService`, `CustomerAnalyticsService`, `ProductAnalyticsService`, `InventoryService`  
- [x] `AnalyticsFilter` / `KPIResult`  
- [x] CLI `analytics kpi|rfm|abc|cohort|trend`  
- [x] Unit tests pure analytics + KPI  

### Checklist

- [x] KPI from lines matches metric defs (revenue/cogs/profit/aov)  
- [x] RFM scores + segments  
- [x] ABC A/B/C + Pareto helper  
- [x] Cohort long matrix + pivot  
- [x] MoM trend helper  
- [ ] Live PG verify CLI after seed (manual)  

### Ưu tiên

**P0**

---

## Phase 7 — Visualization

### Mục tiêu

Library chart Plotly + Matplotlib sẵn sàng cho dashboard & PDF.

### Công việc

1. `styles.py` palette  
2. 8 chart factories Plotly  
3. Matplotlib counterparts cho PDF  
4. Formatters money/percent  
5. Smoke tests figures  

### Deliverables

- [x] `docs/data-visualization.md`  
- [x] `src/app/visualization/styles.py`  
- [x] `src/app/visualization/plotly_charts.py` (8 types)  
- [x] `src/app/visualization/matplotlib_charts.py`  
- [x] Unit smoke tests  

### Checklist

- [x] Line, Bar, Pie, Area, Scatter, Histogram, Heatmap, Treemap  
- [x] Không DB trong package  
- [x] PNG export matplotlib OK (`fig_to_png_bytes` / `save_fig`)  

### Ưu tiên

**P0** (trước dashboard/report polish)

---

## Phase 8 — Dashboard

### Mục tiêu

Streamlit multipage interactive BI.

### Công việc

1. App entry + multipage  
2. Sidebar filters form  
3. Overview KPIs + charts  
4. Sales / Products / Customers / Inventory pages  
5. cache_data  
6. Empty/error states  

### Deliverables

- [x] `docs/dashboard-design.md`  
- [x] `src/app/dashboard/app.py` + multipage `pages/`  
- [x] filters / kpi_cards / charts components  
- [x] cached `data_access.py`  
- [x] CLI `dashboard run`  
- [x] `.streamlit/config.toml`  

### Checklist

- [x] Global filters form (Apply/Reset)  
- [x] ≥ 7 KPIs + period deltas  
- [x] 8 chart types across pages  
- [x] MetricsService for KPIs  
- [x] README launch instructions  
- [ ] Live demo with seeded DB (manual)  

### Ưu tiên

**P0 for portfolio demo**

---

## Phase 9 — Reporting

### Mục tiêu

Daily → Yearly Excel + PDF.

### Công việc

1. ReportDataPackage  
2. Excel builders  
3. PDF builders + fonts VN  
4. Generators 5 types  
5. CLI `report generate`  

### Deliverables

- [x] `docs/reporting-design.md`  
- [x] `src/app/reports/**` periods, package, collector, excel, pdf  
- [x] `ReportService`  
- [x] CLI `report generate`  
- [x] Unit tests (period + excel/pdf sample package)  
- [x] outputs under `output/reports/` (gitignored via output/)  

### Checklist

- [x] Monthly excel multi-sheet (Summary, Trend, rankings, RFM, ABC, Definitions…)  
- [x] Monthly PDF with KPI table + matplotlib charts  
- [x] KPI via MetricsService (same defs as dashboard)  
- [x] daily / weekly / monthly / quarterly / yearly period resolution  
- [ ] Live generate against seeded DB (manual)  

### Ưu tiên

**P0**

---

## Phase 10 — Testing & Hardening

### Mục tiêu

pytest suite, quality tools, docs sync, README polish.

### Công việc

1. Unit + integration + DQ tests  
2. ruff, black, mypy config  
3. README setup end-to-end  
4. Fix gaps from earlier phases  
5. Optional: 100k seed performance notes  

### Deliverables

- [x] `docs/testing-plan.md`  
- [ ] `tests/**`  
- [ ] Root `README.md`  

### Checklist

- [ ] `pytest` green  
- [ ] ruff/black/mypy clean  
- [ ] README: setup PG, migrate, seed, dashboard, report  
- [ ] Portfolio narrative (what/why/how)  

### Ưu tiên

**P0 to close project**

---

## Dependency graph

```text
Phase 1 Docs ──┐
               ├── Phase 2 DB models/migrations
Phase 2 Docs ──┘            │
                            ▼
                     Phase 3 Seed
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
     Phase 4 SQL   Phase 5 ETL   (samples)
          │             │
          └──────┬──────┘
                 ▼
          Phase 6 Analytics
                 │
          ┌──────┴──────┐
          ▼             ▼
   Phase 7 Viz    (metrics ready)
          │
          ├──────────────► Phase 8 Dashboard
          └──────────────► Phase 9 Reporting
                              │
                              ▼
                       Phase 10 Testing
```

SQL catalog (4) có thể song song ETL (5) sau khi có seed.

---

## Ước lượng effort (tham khảo học tập)

| Phase | Effort gợi ý |
|-------|----------------|
| 1 | 1–2 ngày (docs — done) |
| 2 | 2–4 ngày |
| 3 | 2–5 ngày (1m lâu hơn) |
| 4 | 5–10 ngày |
| 5 | 3–6 ngày |
| 6 | 3–5 ngày |
| 7 | 1–3 ngày |
| 8 | 3–6 ngày |
| 9 | 3–6 ngày |
| 10 | 2–4 ngày |

---

## Definition of Done — toàn dự án

Xem `business-requirements.md` §1.8. Tóm tắt:

- Schema + seed multi-scale  
- ≥100 SQL  
- ETL 3 formats  
- Analytics RFM/ABC/Cohort  
- Streamlit dashboard  
- Excel + PDF reports  
- Tests + quality tools  
- Docs đầy đủ  

---

## Cách yêu cầu triển khai

Khi sẵn sàng code, chỉ định rõ phase, ví dụ:

- *“Implement Phase 2: Database — models + Alembic”*  
- *“Làm Phase 3 seed scale 10k”*  
- *“Phase 4: viết Basic SQL B01–B25”*  

Agent sẽ bám deliverables + checklist phase đó, **không viết code ngoài scope** trừ phụ thuộc cứng.
