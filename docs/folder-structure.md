# 8. Folder Structure

Cấu trúc đề xuất cho toàn bộ dự án (sẽ tạo dần theo phase; giai đoạn design chỉ có `docs/`).

```text
sales-dashboard/
├── README.md                 # Hướng dẫn setup & demo (Phase sau)
├── pyproject.toml            # deps, ruff, black, mypy, pytest
├── .env.example
├── .gitignore
├── alembic.ini
│
├── docs/                     # ★ Tài liệu thiết kế (giai đoạn hiện tại)
│   ├── README.md
│   ├── business-requirements.md
│   ├── functional-requirements.md
│   ├── non-functional-requirements.md
│   ├── database-design.md
│   ├── sql-roadmap.md
│   ├── etl-design.md
│   ├── python-architecture.md
│   ├── folder-structure.md
│   ├── dashboard-design.md
│   ├── data-visualization.md
│   ├── reporting-design.md
│   ├── seed-data-design.md
│   ├── testing-plan.md
│   └── development-roadmap.md
│
├── app/                      # Application package
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── engine.py
│   │   └── session.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── mixins.py
│   │   ├── region.py
│   │   ├── store.py
│   │   ├── employee.py
│   │   ├── customer.py
│   │   ├── supplier.py
│   │   ├── brand.py
│   │   ├── category.py
│   │   ├── product.py
│   │   ├── promotion.py
│   │   ├── order.py
│   │   ├── payment.py
│   │   ├── inventory.py
│   │   ├── stock_movement.py
│   │   ├── return_.py          # return is keyword
│   │   └── calendar.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── customer.py
│   │   ├── product.py
│   │   ├── order.py
│   │   ├── filters.py
│   │   └── metrics.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── customer.py
│   │   ├── product.py
│   │   ├── order.py
│   │   ├── inventory.py
│   │   └── analytics.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── metrics_service.py
│   │   ├── customer_analytics_service.py
│   │   ├── product_analytics_service.py
│   │   ├── inventory_service.py
│   │   ├── etl_service.py
│   │   ├── report_service.py
│   │   └── seed_service.py
│   ├── etl/
│   │   ├── __init__.py
│   │   ├── pipeline.py
│   │   ├── manifest.py
│   │   ├── extractors/
│   │   ├── validators/
│   │   ├── cleaning/
│   │   ├── transformers/
│   │   └── loaders/
│   ├── analytics/
│   │   ├── __init__.py
│   │   ├── rfm.py
│   │   ├── abc.py
│   │   ├── cohort.py
│   │   ├── trends.py
│   │   └── descriptive.py
│   ├── visualization/
│   │   ├── __init__.py
│   │   ├── plotly_charts.py
│   │   ├── matplotlib_charts.py
│   │   └── styles.py
│   ├── reports/
│   │   ├── __init__.py
│   │   ├── excel/
│   │   ├── pdf/
│   │   └── generators/
│   ├── dashboard/
│   │   ├── app.py
│   │   ├── pages/
│   │   ├── components/
│   │   └── state.py
│   ├── cli/
│   │   ├── __init__.py
│   │   └── main.py
│   └── utils/
│       ├── __init__.py
│       ├── logging.py
│       ├── dates.py
│       ├── money.py
│       ├── paths.py
│       └── errors.py
│
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│
├── sql/
│   ├── README.md
│   ├── basic/
│   ├── intermediate/
│   ├── advanced/
│   ├── reporting/
│   └── optimization/
│
├── data/
│   ├── raw/
│   │   ├── csv/
│   │   ├── excel/
│   │   ├── json/
│   │   └── samples/
│   ├── staging/
│   ├── rejected/
│   └── archive/
│
├── output/
│   ├── reports/
│   │   ├── excel/
│   │   └── pdf/
│   └── exports/
│
├── logs/                     # gitignored
│
├── scripts/                  # optional helper shell/python one-offs
│   └── dev_bootstrap.md      # or .sh notes without docker
│
└── tests/
    ├── conftest.py
    ├── unit/
    ├── integration/
    └── data_quality/
```

---

## 8.1 Nhiệm vụ từng thư mục gốc

| Path | Nhiệm vụ |
|------|----------|
| `docs/` | Phân tích, thiết kế, roadmap — source of truth thiết kế |
| `app/` | Toàn bộ mã ứng dụng Python |
| `alembic/` | Database migrations |
| `sql/` | Catalog 100+ bài SQL học tập & reporting |
| `data/` | Input files ETL; không commit data lớn |
| `output/` | Báo cáo sinh ra; gitignore nội dung file |
| `logs/` | loguru files |
| `scripts/` | Tiện ích dev không thuộc package |
| `tests/` | pytest |

---

## 8.2 Quy tắc quản lý file

1. **Không commit** `.env`, `logs/`, `output/**/*`, seed dump lớn, `data/rejected/`.  
2. **Commit** `data/raw/samples/` nhỏ (vài chục–vài trăm dòng) để demo ETL.  
3. **SQL** mỗi bài một file, tên `ID_snake_title.sql`.  
4. **Models** một entity chính mỗi file; tránh `models.py` khổng lồ.  
5. **Dashboard pages** đánh số để Streamlit sắp thứ tự.

---

## 8.3 Growth path (không làm sớm)

Khi dự án phình:

- `app/analytics/sql/` load file từ `/sql/reporting`  
- `docs/adr/` Architecture Decision Records  
- Materialized views migration riêng  

Giữ scope phase hiện tại gọn theo roadmap.
