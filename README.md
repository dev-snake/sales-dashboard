# Sales Analytics Dashboard

Portfolio / learning project: **end-to-end retail sales analytics** on Python + PostgreSQL.

```text
CSV/Excel/JSON → ETL → PostgreSQL → SQL catalog (135)
                              ↓
                    Python analytics (RFM, ABC, cohort)
                              ↓
              Streamlit dashboard · Excel/PDF reports
```

> **Status:** Phases 1–10 implemented (design docs + application code + tests).  
> Full design: [`docs/README.md`](docs/README.md).

---

## Why this project

| Goal | How it shows up |
|------|-----------------|
| Learn SQL deeply | 135 catalog queries (basic → window/CTE → RFM/ABC) |
| Practice ETL | Multi-format extract, Pydantic validate, upsert load |
| Clean Python architecture | config → repositories → services → CLI/dashboard |
| BI storytelling | Streamlit multipage + executive Excel/PDF |
| Portfolio demo | One command chain from empty DB → dashboard |

**Out of scope (by design):** Docker, Kafka, Airflow, FastAPI/Django, React, CI/CD.

---

## Tech stack

| Layer | Tools |
|-------|--------|
| Language | Python 3.13+ |
| DB | PostgreSQL, psycopg, SQLAlchemy 2.x, Alembic |
| Analysis | pandas, numpy |
| Viz / BI | Plotly, Matplotlib, Streamlit |
| Reports | openpyxl, reportlab |
| Quality | Ruff, Black, mypy, pytest |

---

## Quick start (end-to-end)

### 1. Environment

```bash
cd sales-dashboard
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -U pip
pip install -e ".[dev]"
cp .env.example .env
# Edit DATABASE_URL to match your local PostgreSQL
```

### 2. Database

```sql
CREATE DATABASE sales_dashboard;
-- optional: CREATE DATABASE sales_dashboard_test;
```

```bash
sales-dashboard db ping
sales-dashboard db migrate
```

### 3. Seed synthetic data

```bash
sales-dashboard seed run --scale 1k --seed 42 --reset --yes
# scales: 100 | 1k | 10k | 100k | 1m
```

### 4. Explore SQL / analytics / reports / dashboard

```bash
sales-dashboard sql list
sales-dashboard sql run R01

sales-dashboard analytics kpi --days 30
sales-dashboard analytics rfm

sales-dashboard report generate --type monthly --format both

sales-dashboard dashboard run
# → http://localhost:8501
```

### 5. ETL samples (optional)

```bash
sales-dashboard etl run-all --samples
```

---

## Project layout

```text
sales-dashboard/
├── docs/                 # Design & conventions
├── src/app/              # Application package
│   ├── config/ database/ models/ schemas/
│   ├── repositories/ services/
│   ├── etl/ analytics/ visualization/
│   ├── dashboard/ reports/ seed/ sql_catalog/ cli/
├── alembic/              # Migrations
├── sql/                  # 135 SQL exercises
├── datasets/             # raw / cleaned / processed / exported
├── tests/                # unit · integration · data_quality
├── scripts/quality.sh    # local quality gate
├── pyproject.toml
└── README.md
```

---

## CLI map

| Command | Purpose |
|---------|---------|
| `db ping / migrate / tables` | Database |
| `seed run / samples` | Synthetic data + ETL samples |
| `etl run / run-all` | File → PostgreSQL |
| `sql list / show / run` | SQL catalog |
| `analytics kpi/rfm/abc/…` | Python analytics |
| `dashboard run` | Streamlit BI |
| `report generate` | Excel + PDF |

---

## How to test

### Unit only (default, no DB)

```bash
pytest -q -m "not integration and not data_quality"
# or
bash scripts/quality.sh
```

### With PostgreSQL

```bash
export TEST_DATABASE_URL=postgresql+psycopg://USER:PASS@localhost:5432/sales_dashboard_test
# or reuse DATABASE_URL
pytest -q -m integration
# after seed on that DB:
pytest -q -m data_quality
# everything:
RUN_INTEGRATION=1 bash scripts/quality.sh
```

### Quality tools

```bash
ruff check src tests
black --check src tests
mypy
pytest -q
```

Markers: `unit` · `integration` · `data_quality` (see `docs/testing-plan.md`).

---

## Documentation index

| Doc | Content |
|-----|---------|
| [docs/README.md](docs/README.md) | Full design index |
| [business-requirements.md](docs/business-requirements.md) | Personas & goals |
| [database-design.md](docs/database-design.md) | 3NF schema + ERD |
| [sql-roadmap.md](docs/sql-roadmap.md) | 135 SQL plan |
| [etl-design.md](docs/etl-design.md) | ETL pipeline |
| [dashboard-design.md](docs/dashboard-design.md) | Streamlit UX |
| [reporting-design.md](docs/reporting-design.md) | Excel/PDF reports |
| [testing-plan.md](docs/testing-plan.md) | Test strategy |
| [coding-conventions.md](docs/coding-conventions.md) | Style rules |
| [development-roadmap.md](docs/development-roadmap.md) | 10 phases |

---

## Roadmap status

| Phase | Status |
|-------|--------|
| Docs / Business analysis | ✅ |
| Project scaffold | ✅ |
| Database models + Alembic | ✅ |
| Seed data (multi-scale) | ✅ |
| SQL catalog (135) | ✅ |
| ETL CSV/Excel/JSON | ✅ |
| Python analytics | ✅ |
| Visualization (Plotly/MPL) | ✅ |
| Streamlit dashboard | ✅ |
| Excel + PDF reporting | ✅ |
| Testing & hardening | ✅ |

---

## Data privacy

Seed/ETL samples use **Faker synthetic data only** — no real customer PII.

---

## License

MIT — learning & portfolio use.
