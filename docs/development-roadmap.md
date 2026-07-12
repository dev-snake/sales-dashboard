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
- [ ] Seed generators + CLI  
- [ ] `data/raw/samples/*`  

### Checklist

- [ ] Scale 100 & 1k & 10k chạy OK  
- [ ] 100k documented (có thể chạy lâu)  
- [ ] Invariants DQ01–DQ10 pass ở XS  
- [ ] Seasonality quan sát được bằng SQL đơn giản  

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
- [ ] `sql/**/*.sql`  
- [ ] `sql/README.md`  

### Checklist

- [ ] ≥ 100 queries  
- [ ] Reporting R01–R30 chạy trên seed  
- [ ] EXPLAIN notes tối thiểu 5 cases  
- [ ] Metric definitions đồng bộ docs  

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
- [ ] `app/etl/**`  
- [ ] sample raw files  

### Checklist

- [ ] Load customers/products/orders từ samples  
- [ ] Invalid rows → rejected file  
- [ ] Idempotent re-run masters (upsert)  
- [ ] loguru metrics rows read/loaded  

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

- [x] `docs/python-architecture.md` (partial)  
- [ ] `app/services/*` `app/analytics/*`  

### Checklist

- [ ] KPI numbers match SQL R01/R02 on fixture  
- [ ] RFM segments populated  
- [ ] ABC labels A/B/C  
- [ ] Cohort matrix shape correct  

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
- [ ] `app/visualization/*`  

### Checklist

- [ ] Mỗi chart type 1 factory  
- [ ] Không DB trong package  
- [ ] PNG export matplotlib OK  

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
- [ ] `app/dashboard/**`  

### Checklist

- [ ] All global filters work  
- [ ] ≥ 7 KPIs  
- [ ] 8 chart types xuất hiện  
- [ ] MetricsService only for KPIs  
- [ ] Demo script in README  

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
- [ ] `app/reports/**`  
- [ ] sample outputs gitignored  

### Checklist

- [ ] Monthly excel ≥ 8 sheets  
- [ ] Monthly PDF opens, Unicode OK  
- [ ] KPI match dashboard for same period  
- [ ] daily/weekly/quarterly/yearly runnable  

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
