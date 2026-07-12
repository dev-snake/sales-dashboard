# Phase 1 — Project Scaffold: Ghi chú so với tài liệu thiết kế

Tài liệu nghiệp vụ trong `docs/` **không bị thay đổi**. Phase này chỉ khởi tạo khung mã nguồn.

## 1. Đánh số phase

| Nguồn | “Phase 1” nghĩa là |
|-------|---------------------|
| `docs/development-roadmap.md` | Business Analysis (đã xong dưới dạng docs) |
| Yêu cầu triển khai hiện tại | **Project Scaffold** (bộ khung code) |

→ Scaffold này tương ứng phần “khởi tạo project” từng nằm ở đầu Phase 2 (implementation) trong roadmap. Roadmap nghiệp vụ vẫn giữ nguyên; khi implement DB models sẽ gọi là **Phase 2 — Database Models**.

## 2. Package layout: `app/` vs `src/`

| Docs (`folder-structure.md`) | Yêu cầu scaffold | Quyết định |
|------------------------------|------------------|------------|
| Package tại `app/` (root) | Modules trong `src/` | **`src/app/`** (src-layout) |

- Import giữ nguyên như kiến trúc: `from app.config import settings`
- `pyproject.toml` dùng `[tool.setuptools.packages.find] where = ["src"]`

## 3. Thư mục dữ liệu: `data/` vs `datasets/`

| Docs (`etl-design.md`) | Yêu cầu scaffold | Quyết định |
|------------------------|------------------|------------|
| `data/raw`, `staging`, `rejected`, `archive` + `output/reports` | `datasets/raw`, `cleaned`, `processed`, `exported` | **`datasets/`** theo scaffold |

Ánh xạ ý nghĩa (sẽ dùng ở phase ETL):

| Scaffold | Tương đương docs |
|----------|------------------|
| `datasets/raw/` | `data/raw/` |
| `datasets/cleaned/` | `data/staging/` (cleaned) |
| `datasets/processed/` | dữ liệu đã transform sẵn sàng load |
| `datasets/exported/` | `output/` / export báo cáo & dump |

Có thể bổ sung `datasets/rejected/` ở phase ETL nếu cần file reject.

## 4. Thư mục `database/` (root)

Docs đặt migrations tại `alembic/` (chuẩn Alembic). Scaffold có thêm `database/` ở root để:

- Ghi chú kết nối / checklist local PostgreSQL
- Chỗ chứa artifact SQL thủ công sau này (không thay Alembic)

Alembic vẫn ở `alembic/` + `alembic.ini` (root).

## 5. Modules stub

Các package `models`, `repositories`, `services`, `etl`, `analytics`, `visualization`, `dashboard`, `reports` chỉ chứa `__init__.py` + docstring — **chưa có business logic**, đúng yêu cầu scaffold.

## 6. Không mâu thuẫn nghiệp vụ

Tech stack, cấm Docker/CI/web framework, schema 16 bảng, metric definitions — giữ nguyên trong docs. Scaffold không redefine business rules.
