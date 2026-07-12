# Sales Analytics Dashboard

Hệ thống phân tích doanh số bán lẻ (portfolio / học tập): thu thập → làm sạch → lưu PostgreSQL → phân tích SQL/Python → dashboard Streamlit → xuất Excel/PDF.

> **Trạng thái hiện tại:** Project scaffold (khung dự án).  
> Nghiệp vụ, ETL, Analytics, Dashboard, Report **chưa** triển khai.  
> Thiết kế đầy đủ nằm trong [`docs/`](docs/README.md).

---

## Giới thiệu

Dự án mô phỏng chuỗi bán lẻ multi-store với:

- Schema PostgreSQL chuẩn 3NF (16 bảng + calendar)
- ETL từ CSV / Excel / JSON
- 100+ bài SQL (basic → advanced → reporting)
- Analytics (RFM, ABC, cohort, …)
- Dashboard tương tác (Streamlit)
- Báo cáo Excel & PDF

**Không dùng:** Docker, Kafka, Airflow, FastAPI/Django/Flask, React, CI/CD (xem docs).

---

## Công nghệ

| Lớp | Stack |
|-----|--------|
| Language | Python **3.13+** |
| Database | PostgreSQL + **psycopg** + **SQLAlchemy 2.x** + **Alembic** |
| Analysis | pandas, numpy |
| Viz / BI | Plotly, Matplotlib, Streamlit |
| Reports | openpyxl, reportlab |
| Config | python-dotenv, pydantic-settings, pydantic |
| Logging | loguru |
| CLI | Typer |
| Fake data | Faker (phase sau) |
| Quality | Ruff, Black, mypy, pytest |

---

## Cấu trúc thư mục

```text
sales-dashboard/
├── docs/                 # Tài liệu thiết kế & conventions
├── src/app/              # Mã nguồn chính (package: app)
│   ├── config/           # Settings (pydantic-settings)
│   ├── database/         # Engine, session, Base
│   ├── models/           # ORM models (stub — Phase 2)
│   ├── schemas/          # Pydantic DTOs (stub)
│   ├── repositories/     # Data access (stub)
│   ├── services/         # Use-cases (stub)
│   ├── etl/              # ETL pipeline (stub)
│   ├── analytics/        # Python analytics (stub)
│   ├── visualization/    # Charts (stub)
│   ├── dashboard/        # Streamlit (stub)
│   ├── reports/          # Excel/PDF (stub)
│   ├── cli/              # Typer CLI
│   └── utils/            # Logging, errors, paths
├── alembic/              # Database migrations
├── database/             # Ghi chú setup PostgreSQL
├── sql/                  # Catalog SQL (Phase 4)
├── datasets/             # Dữ liệu file
│   ├── raw/              # Nguồn thô (csv/excel/json)
│   ├── cleaned/          # Đã làm sạch
│   ├── processed/        # Sẵn sàng load
│   └── exported/         # Export / báo cáo
├── tests/                # pytest
├── logs/                 # Log files (gitignore nội dung)
├── pyproject.toml
├── requirements.txt
├── .env.example
└── README.md
```

### Nhiệm vụ từng nhóm thư mục

| Path | Nhiệm vụ |
|------|----------|
| `docs/` | Business analysis, DB design, SQL roadmap, conventions |
| `src/app/config` | Đọc `.env`, Settings dùng toàn app |
| `src/app/database` | Kết nối PostgreSQL, session scope, DeclarativeBase |
| `src/app/models` | SQLAlchemy models (chưa có bảng) |
| `src/app/repositories` | Truy vấn DB cô lập |
| `src/app/services` | Business orchestration |
| `src/app/etl` | Extract → validate → clean → transform → load |
| `src/app/analytics` | RFM, ABC, cohort, trends |
| `src/app/visualization` | Plotly / Matplotlib factories |
| `src/app/dashboard` | Streamlit UI |
| `src/app/reports` | Excel / PDF generators |
| `src/app/cli` | Entry Typer |
| `src/app/utils` | Cross-cutting helpers |
| `datasets/` | Vòng đời file dữ liệu |
| `sql/` | Bài tập & reporting SQL |
| `alembic/` | Versioned schema migrations |
| `tests/` | Unit / integration / data quality |

Chi tiết conflict docs vs scaffold: [`docs/phase1-scaffold-notes.md`](docs/phase1-scaffold-notes.md).  
Coding rules: [`docs/coding-conventions.md`](docs/coding-conventions.md).

---

## Yêu cầu hệ thống

- Python **3.13+**
- PostgreSQL **15+** (cho `db ping` / phases sau)
- pip / venv

---

## Cài đặt

```bash
# 1. Clone / vào thư mục project
cd sales-dashboard

# 2. Tạo virtualenv
python3.13 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Cài package ở chế độ editable + dev tools
pip install -U pip
pip install -e ".[dev]"

# (tuỳ chọn) hoặc:
# pip install -r requirements.txt
# pip install -e .
```

```bash
# 4. Cấu hình môi trường
cp .env.example .env
# Chỉnh DATABASE_URL cho máy bạn
```

```bash
# 5. Tạo database PostgreSQL (một lần)
# psql -U postgres -c "CREATE DATABASE sales_dashboard;"
```

---

## Cách chạy (scaffold)

```bash
# Phiên bản
sales-dashboard version
# hoặc
python -m app version

# Xem cấu hình (password đã mask)
sales-dashboard info

# Kiểm tra kết nối PostgreSQL
sales-dashboard db ping

# Help đầy đủ
sales-dashboard --help
sales-dashboard db --help
```

Các lệnh `etl`, `seed`, `report`, `sql` hiện là **stub** (in thông báo, chưa có logic).

### Quality tools

```bash
ruff check src tests
black src tests
mypy
pytest
```

### Database (Phase 2)

```bash
# Đảm bảo PostgreSQL chạy và DATABASE_URL trong .env đúng
sales-dashboard db ping
sales-dashboard db migrate    # alembic upgrade head
sales-dashboard db current
sales-dashboard db tables     # 16 tables
sales-dashboard db downgrade  # optional: -1
```

### Seed data (Phase 3)

```bash
# Chỉ export file mẫu ETL (không cần DB)
sales-dashboard seed samples

# Seed vào PostgreSQL (cần migrate trước)
sales-dashboard seed run --scale 100 --seed 42
sales-dashboard seed run --scale 10k --reset --yes

# Scale: 100 | 1k | 10k | 100k | 1m
```

Dữ liệu là **synthetic** (Faker) — không chứa liệu khách hàng thật.

### SQL catalog (Phase 4)

```bash
sales-dashboard sql list
sales-dashboard sql list --level advanced
sales-dashboard sql show R04
sales-dashboard sql run R01          # cần DB + seed
sales-dashboard sql run I14 --limit 20
```

Chi tiết: [`sql/README.md`](sql/README.md), metrics: [`sql/metrics.md`](sql/metrics.md).

### ETL (Phase 5)

```bash
# Load full sample pack (CSV + Excel + JSON) in FK order
sales-dashboard etl run-all --samples

# Or one entity
sales-dashboard etl run -e customers -f datasets/raw/samples/customers.csv --ensure-masters

# Manifest
sales-dashboard etl run-all --manifest datasets/manifest.example.yaml
```

Contracts: [`docs/data-contracts.md`](docs/data-contracts.md). Rejects: `datasets/rejected/`.

### Analytics (Phase 6)

```bash
# Cần DB + seed/ETL
sales-dashboard analytics kpi --days 30
sales-dashboard analytics rfm --days 365
sales-dashboard analytics abc --days 90
sales-dashboard analytics cohort --days 365
sales-dashboard analytics trend --days 180
```

KPI definitions align with [`sql/metrics.md`](sql/metrics.md) (paid/completed + line_total).

### Dashboard (Phase 8)

```bash
# Cần migrate + seed
sales-dashboard dashboard run
# or
PYTHONPATH=src streamlit run src/app/dashboard/app.py
```

Pages: **Overview** · **Sales** · **Products** · **Customers** · **Inventory**  
Sidebar filters (form Apply/Reset) · 7 KPI cards with period deltas · Plotly charts.

---

## Cấu hình công cụ

| Tool | File | Mục đích |
|------|------|----------|
| Ruff | `pyproject.toml` `[tool.ruff]` | Lint nhanh + isort (E,W,F,I,B,UP,…) |
| Black | `[tool.black]` | Format thống nhất, line-length 100 |
| mypy | `[tool.mypy]` | Type-check package `app` (strict-ish) |
| pytest | `[tool.pytest.ini_options]` | `testpaths=tests`, markers unit/integration |

---

## Roadmap

Theo [`docs/development-roadmap.md`](docs/development-roadmap.md) (điều chỉnh nhãn scaffold):

| Phase | Nội dung | Trạng thái |
|-------|----------|------------|
| Docs / BA | Business & design docs | ✅ |
| **Scaffold** | Cấu trúc project, config, CLI, DB connection | ✅ |
| **Database models** | SQLAlchemy + Alembic schema 16 bảng | ✅ |
| **Seed data** | Faker multi-scale + sample export | ✅ |
| **SQL catalog** | 135 queries + CLI runner | ✅ |
| **ETL** | CSV/Excel/JSON → PostgreSQL | ✅ |
| **Analytics** | MetricsService, RFM, ABC, cohort, trends | ✅ |
| **Visualization** | Plotly 8 types + Matplotlib PDF helpers | ✅ |
| **Dashboard** | Streamlit multipage BI | ✅ |
| Reporting | Excel + PDF | ⏳ |
| Testing | Mở rộng coverage | ⏳ |

---

## Tài liệu

- [Tổng mục docs](docs/README.md)
- [Business requirements](docs/business-requirements.md)
- [Database design](docs/database-design.md)
- [SQL roadmap](docs/sql-roadmap.md)
- [ETL design](docs/etl-design.md)
- [Coding conventions](docs/coding-conventions.md)
- [Scaffold notes](docs/phase1-scaffold-notes.md)

---

## License

MIT (portfolio / learning project).
