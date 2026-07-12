# Coding Conventions

Áp dụng cho toàn bộ mã nguồn `src/app` và `tests/`.

---

## 1. Naming Convention

| Thành phần | Quy tắc | Ví dụ |
|------------|---------|--------|
| Package / module | `snake_case` | `metrics_service.py` |
| Class | `PascalCase` | `OrderRepository` |
| Function / method | `snake_case` | `get_session` |
| Constant | `UPPER_SNAKE` | `PROJECT_ROOT` |
| Private | tiền tố `_` | `_get_session_factory` |
| Type alias | `PascalCase` | `AnalyticsFilter` |
| SQL file | `{ID}_{snake_title}.sql` | `R04_top_products.sql` |
| DB table / column | `snake_case`, bảng số nhiều | `order_items.line_total` |
| Env var | `UPPER_SNAKE` | `DATABASE_URL` |
| CLI command | `kebab` groups, verbs | `db ping`, `seed run` |

---

## 2. Folder Convention

- Mã ứng dụng chỉ nằm trong `src/app/`.
- Tests mirror theo lớp: `tests/unit`, `tests/integration`, `tests/data_quality`.
- SQL học tập / reporting trong `sql/{basic,intermediate,advanced,reporting,optimization}/`.
- Dữ liệu file trong `datasets/{raw,cleaned,processed,exported}/` — không commit bulk data.
- Tài liệu thiết kế trong `docs/`.
- Migrations trong `alembic/versions/` — không sửa revision đã apply trên máy khác nếu đã share.
- Không đặt business logic trong `cli/` hay `dashboard/` (mỏng); gọi `services/`.

---

## 3. Import Convention

Thứ tự (Ruff isort / I):

1. Stdlib  
2. Third-party  
3. First-party `app.*`

```python
from __future__ import annotations

import json
from pathlib import Path

from loguru import logger
from sqlalchemy import select

from app.config import get_settings
from app.database.session import session_scope
```

- Prefer absolute imports: `from app.utils.errors import AppError`
- Tránh circular imports: models không import services; services import repositories.
- `TYPE_CHECKING` blocks cho type-only imports khi cần.

---

## 4. Type Hint Convention

- Python 3.13+: dùng built-in generics (`list[str]`, `dict[str, int]`).
- Mọi public function **bắt buộc** annotate params + return.
- Prefer `X | None` thay `Optional[X]`.
- Dùng `from __future__ import annotations` ở module mới.
- Pydantic models cho I/O validation; SQLAlchemy Mapped[] cho ORM (phase models).
- mypy: `disallow_untyped_defs = true` trên package `app`.

---

## 5. Exception Convention

```text
AppError
├── ConfigError
├── DatabaseError
├── ValidationError
├── ETLError
├── ReportError
└── NotFoundError
```

- Raise domain errors với message rõ + optional `details=dict`.
- Không dùng bare `except:`.
- CLI / dashboard bắt `AppError` ở biên, log full stack với loguru, user message ngắn.
- Không nuốt exception im lặng.

---

## 6. Logging Convention

- Dùng **loguru** (`from loguru import logger`), không `print` trong library code.
- Levels: DEBUG dev detail · INFO lifecycle · WARNING recoverable · ERROR failures.
- Message dạng: `"Loaded customers | rows={} duration_ms={}"` với bind args.
- Không log password / full connection string có secret (mask như CLI `info`).
- ETL (sau này): luôn log rows_read / valid / rejected / loaded.

`setup_logging()` gọi một lần từ CLI callback / app entry.

---

## 7. SQL Convention

- Keywords SQL: `UPPER CASE` (`SELECT`, `FROM`, `WHERE`).
- Identifiers: `snake_case`.
- Một file một bài / một report query chính.
- Header comment:

```sql
-- ID: R04
-- Title: Top products by revenue
-- Skills: JOIN, GROUP BY, ORDER BY
-- Tables: order_items, products, orders
```

- Parameterized queries only khi gọi từ Python (`text()` + binds) — cấm f-string SQL với input user.
- Metrics: chỉ `status IN ('paid', 'completed')` cho revenue (docs).
- Soft-delete masters: `deleted_at IS NULL` mặc định.

---

## 8. Code quality tools

| Tool | Vai trò | Lệnh |
|------|---------|------|
| **Ruff** | Lint + import sort | `ruff check src tests` |
| **Black** | Format | `black src tests` |
| **mypy** | Static types | `mypy` |
| **pytest** | Tests | `pytest` |

Line length: **100**. Target: **py313**.

---

## 9. Git / secrets

- Không commit `.env`, dumps lớn, `logs/*`.
- Commit `.env.example` và sample data nhỏ trong `datasets/raw/samples/` (khi có).
