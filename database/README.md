# database/

Thư mục hỗ trợ vận hành PostgreSQL **bên cạnh** Alembic.

| Thành phần | Vai trò |
|------------|---------|
| `alembic/` + `alembic.ini` (root project) | **Nguồn sự thật** cho schema migrations |
| `database/` | Ghi chú setup local, checklist, (tùy chọn) script SQL thủ công |

## Checklist PostgreSQL local

1. Cài PostgreSQL 15+ (khuyến nghị 16).
2. Tạo database:

```sql
CREATE DATABASE sales_dashboard;
```

3. Copy `.env.example` → `.env` và chỉnh `DATABASE_URL`:

```text
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@localhost:5432/sales_dashboard
```

4. Kiểm tra kết nối:

```bash
sales-dashboard db ping
# hoặc
python -m app.cli.main db ping
```

5. Chạy migration (Phase 2 — models đã sẵn sàng):

```bash
# Tạo database nếu chưa có
# CREATE DATABASE sales_dashboard;

sales-dashboard db ping
sales-dashboard db migrate
sales-dashboard db current
sales-dashboard db tables
```

Tương đương:

```bash
alembic upgrade head
alembic current
```

## Schema (Phase 2)

| Bảng | Ghi chú |
|------|---------|
| regions, stores, employees, customers | Master + soft delete |
| suppliers, brands, categories, products | Catalog |
| promotions | Discount campaigns |
| orders, order_items, payments | Transactions |
| inventory, stock_movements, returns | Inventory & returns |
| calendar | Date dimension (date_id = YYYYMMDD) |

Trigger `set_updated_at()` gắn trên mọi bảng có `updated_at` (trừ `calendar`).

Revision Alembic: `alembic/versions/20260712_0001_initial_schema.py`

## Lưu ý

- Không dùng Docker trong phạm vi dự án (theo docs).
- Không commit mật khẩu thật.
- Schema chi tiết: `docs/database-design.md`.
- ERD Mermaid: `docs/erd.mmd`.
