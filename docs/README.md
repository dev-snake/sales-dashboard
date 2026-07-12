# Sales Analytics Dashboard — Tài liệu thiết kế

> **Dự án học tập & portfolio** mô phỏng hệ thống phân tích doanh số bán lẻ thực tế.  
> Giai đoạn hiện tại: **Phân tích & Thiết kế** — chưa có mã nguồn ứng dụng.

---

## Mục tiêu tài liệu

Bộ tài liệu này đủ chi tiết để triển khai từng phase mà không cần thiết kế lại kiến trúc. Mọi quyết định nghiệp vụ, schema, ETL, SQL roadmap, dashboard và kế hoạch phát triển đều được ghi rõ tại đây.

---

## Danh mục tài liệu

| # | File | Nội dung |
|---|------|----------|
| 1 | [business-requirements.md](./business-requirements.md) | Bài toán doanh nghiệp, persona, quy trình, vấn đề & giá trị dashboard |
| 2 | [functional-requirements.md](./functional-requirements.md) | Danh sách chức năng đầy đủ và mô tả chi tiết |
| 3 | [non-functional-requirements.md](./non-functional-requirements.md) | Performance, security, reliability, data quality, logging… |
| 4 | [database-design.md](./database-design.md) | Schema 3NF, PK/FK/index/constraint, ERD, giải thích quan hệ |
| 5 | [sql-roadmap.md](./sql-roadmap.md) | Kế hoạch 100+ bài toán SQL (Basic → Advanced → Reporting → Optimization) |
| 6 | [etl-design.md](./etl-design.md) | Pipeline Extract → Validate → Clean → Transform → Load → Analytics |
| 7 | [python-architecture.md](./python-architecture.md) | Kiến trúc module Python, trách nhiệm từng package |
| 8 | [folder-structure.md](./folder-structure.md) | Cấu trúc thư mục chuẩn toàn dự án |
| 9 | [dashboard-design.md](./dashboard-design.md) | Layout Streamlit, KPI, charts, filters |
| 10 | [data-visualization.md](./data-visualization.md) | Khi dùng Plotly/Matplotlib, mapping KPI → chart type |
| 11 | [reporting-design.md](./reporting-design.md) | Báo cáo Daily/Weekly/Monthly/Quarterly/Yearly, Excel & PDF |
| 12 | [seed-data-design.md](./seed-data-design.md) | Chiến lược dữ liệu giả, quy mô 100 → 1.000.000 records |
| 13 | [testing-plan.md](./testing-plan.md) | Unit, Integration, Data Validation tests |
| 14 | [development-roadmap.md](./development-roadmap.md) | 10 phases: mục tiêu, tasks, deliverables, checklist |
| 15 | [coding-conventions.md](./coding-conventions.md) | Naming, import, typing, logging, SQL conventions |
| 16 | [phase1-scaffold-notes.md](./phase1-scaffold-notes.md) | Ghi chú mâu thuẫn docs vs scaffold implementation |

---

## Tech Stack (đã chốt)

| Lớp | Công nghệ |
|-----|-----------|
| Language | Python 3.13+ |
| Database | PostgreSQL |
| Driver | psycopg |
| ORM | SQLAlchemy 2.x |
| Migration | Alembic |
| Analysis | pandas, numpy |
| Visualization | Plotly, Matplotlib |
| Dashboard | Streamlit |
| Excel / PDF | openpyxl, reportlab |
| Config | python-dotenv, pydantic-settings |
| Validation | pydantic |
| Logging | loguru |
| CLI | Typer |
| Fake data | Faker |
| Testing | pytest |
| Quality | Ruff, Black, mypy |

### Cấm dùng

Docker, Docker Compose, Kubernetes, Redis, Celery, Kafka, RabbitMQ, Airflow, Spark, Dask, FastAPI, Django, Flask, React/Next.js/Vue, CI/CD.

---

## Nguyên tắc triển khai

1. **Không viết code** cho đến khi được yêu cầu theo từng phase.
2. **SQL-first**: PostgreSQL và SQL là trọng tâm học tập.
3. **Module hóa**: mỗi package có ranh giới trách nhiệm rõ.
4. **Data quality**: validate trước khi load; soft-delete và audit timestamps nhất quán.
5. **Portfolio-ready**: README, docs, seed data, demo script phải kể được câu chuyện end-to-end.

---

## Luồng dữ liệu tổng quát

```
CSV / Excel / JSON
        │
        ▼
   Extract (ETL)
        │
        ▼
   Validation (Pydantic)
        │
        ▼
   Cleaning & Transformation
        │
        ▼
   Load → PostgreSQL
        │
        ├──────────────┬────────────────┐
        ▼              ▼                ▼
  SQL Analytics  Python Analytics  Reporting
        │              │                │
        └──────┬───────┘                │
               ▼                        ▼
         Streamlit Dashboard      Excel / PDF
```

---

## Cách dùng tài liệu khi code

1. Đọc `development-roadmap.md` để biết phase hiện tại.
2. Mở tài liệu chuyên đề tương ứng (DB, ETL, Dashboard…).
3. Implement đúng deliverables và đánh dấu checklist.
4. Không mở rộng scope ngoài phase đang yêu cầu.

---

## Trạng thái

| Hạng mục | Trạng thái |
|----------|-----------|
| Phân tích nghiệp vụ | ✅ Hoàn thành (docs) |
| Thiết kế database | ✅ Hoàn thành (docs) |
| SQL roadmap | ✅ Hoàn thành (docs) |
| ETL / Python / Dashboard / Report | ✅ Hoàn thành (docs) |
| Project scaffold | ✅ |
| Database models | ✅ |
| Seed data | ✅ |
| SQL catalog (135) | ✅ |
| ETL pipeline | ✅ |
| Python analytics | ✅ |
| Visualization | ✅ |
| Dashboard | ✅ |
| Reporting | ⏳ |
