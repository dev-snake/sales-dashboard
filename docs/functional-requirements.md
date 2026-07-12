# 2. Functional Requirements

Mỗi chức năng có **ID**, **mô tả**, **actor**, **input/output**, **ưu tiên** (P0 = must, P1 = should, P2 = nice-to-have).

---

## 2.1 Master Data Management

### FR-MD-01 — Quản lý khách hàng (Customers)

| | |
|--|--|
| **Mô tả** | Lưu và truy vấn thông tin khách hàng: mã, tên, email, phone, địa chỉ, region, ngày đăng ký, trạng thái |
| **Actor** | Analyst, System (ETL), Dashboard |
| **Input** | Seed / CSV import / manual record (qua ETL) |
| **Output** | Bản ghi `customers`; dùng cho RFM, CLV, top customers |
| **Priority** | P0 |
| **Ghi chú** | Email/phone unique khi not null; hỗ trợ soft delete |

### FR-MD-02 — Quản lý sản phẩm (Products)

| | |
|--|--|
| **Mô tả** | SKU, tên, category, brand, supplier, giá bán, giá vốn, đơn vị, trạng thái active |
| **Actor** | Ops, ETL |
| **Output** | `products` join category/brand/supplier |
| **Priority** | P0 |

### FR-MD-03 — Quản lý danh mục (Categories)

| | |
|--|--|
| **Mô tả** | Cây danh mục đơn giản (parent_id optional) hoặc flat list + parent |
| **Priority** | P0 |
| **Ghi chú** | Hỗ trợ parent_id self-FK để demo recursive CTE |

### FR-MD-04 — Quản lý thương hiệu (Brands)

| | |
|--|--|
| **Mô tả** | Tên brand, mô tả, quốc gia (optional) |
| **Priority** | P0 |

### FR-MD-05 — Quản lý nhà cung cấp (Suppliers)

| | |
|--|--|
| **Mô tả** | Tên, contact, email, phone, địa chỉ, rating |
| **Priority** | P0 |

### FR-MD-06 — Quản lý cửa hàng (Stores)

| | |
|--|--|
| **Mô tả** | Mã cửa hàng, tên, địa chỉ, region_id, ngày mở, trạng thái |
| **Priority** | P0 |

### FR-MD-07 — Quản lý nhân viên (Employees)

| | |
|--|--|
| **Mô tả** | Họ tên, email, phone, store_id, chức danh, ngày vào làm, manager_id (self-FK) |
| **Priority** | P0 |
| **Ghi chú** | Self-FK phục vụ recursive CTE org chart |

### FR-MD-08 — Quản lý vùng (Regions)

| | |
|--|--|
| **Mô tả** | Mã vùng, tên, cấp (province/city/area) |
| **Priority** | P0 |

### FR-MD-09 — Calendar dimension

| | |
|--|--|
| **Mô tả** | Bảng `calendar` theo ngày: year, quarter, month, week, day_name, is_weekend, is_holiday |
| **Priority** | P0 |
| **Lý do** | Báo cáo thời gian ổn định, tránh extract lặp từ timestamp |

---

## 2.2 Transaction Management

### FR-TX-01 — Quản lý đơn hàng (Orders)

| | |
|--|--|
| **Mô tả** | Header đơn: customer, store, employee, order_date, status, subtotal, discount, tax, total, promo |
| **Status** | `pending`, `paid`, `completed`, `cancelled` |
| **Priority** | P0 |

### FR-TX-02 — Chi tiết đơn hàng (Order Items)

| | |
|--|--|
| **Mô tả** | product_id, quantity, unit_price, unit_cost, discount_amount, line_total |
| **Priority** | P0 |
| **Constraint** | quantity > 0; unit_price ≥ 0; line_total ≥ 0 |

### FR-TX-03 — Thanh toán (Payments)

| | |
|--|--|
| **Mô tả** | Gắn order_id; method (cash, card, transfer, e-wallet); amount; paid_at; status |
| **Priority** | P0 |
| **Ghi chú** | Một order có thể nhiều payment (partial) |

### FR-TX-04 — Khuyến mãi (Promotions)

| | |
|--|--|
| **Mô tả** | Mã promo, loại (percent/fixed), giá trị, start/end date, min_order, active |
| **Priority** | P1 |
| **Liên kết** | `orders.promotion_id` nullable |

### FR-TX-05 — Đổi trả (Returns)

| | |
|--|--|
| **Mô tả** | return header + liên kết order_item; quantity; reason; status; refund_amount |
| **Priority** | P1 |

---

## 2.3 Inventory

### FR-INV-01 — Tồn kho (Inventory)

| | |
|--|--|
| **Mô tả** | Snapshot quantity theo (store_id, product_id); reorder_level; max_level |
| **Priority** | P0 |
| **Unique** | (store_id, product_id) |

### FR-INV-02 — Chuyển động kho (Stock Movements)

| | |
|--|--|
| **Mô tả** | Lịch sử: movement_type (purchase_in, sale_out, return_in, transfer_in/out, adjustment); quantity; reference; moved_at |
| **Priority** | P0 |
| **Ghi chú** | quantity signed hoặc absolute + direction — chốt **signed quantity** (+ in, − out) |

---

## 2.4 Data Ingestion & Quality

### FR-ETL-01 — Import dữ liệu

| | |
|--|--|
| **Mô tả** | Import từ CSV, Excel (.xlsx), JSON vào staging rồi load production tables |
| **Actor** | Developer / Analyst via CLI |
| **Priority** | P0 |

### FR-ETL-02 — Validation

| | |
|--|--|
| **Mô tả** | Schema validation (Pydantic): kiểu, range, required, FK existence (ở load stage) |
| **Output** | valid rows + reject log |
| **Priority** | P0 |

### FR-ETL-03 — Data cleaning

| | |
|--|--|
| **Mô tả** | Trim, standardize phone/email, parse dates, fill default, dedupe keys |
| **Priority** | P0 |

### FR-ETL-04 — Transformation

| | |
|--|--|
| **Mô tả** | Map columns, derive fields (line_total, full_name), normalize enums, timezone-naive UTC/local policy |
| **Priority** | P0 |

### FR-ETL-05 — Load PostgreSQL

| | |
|--|--|
| **Mô tả** | Upsert/insert theo natural key; transaction batch; logging số rows |
| **Priority** | P0 |

### FR-ETL-06 — Seed data generator

| | |
|--|--|
| **Mô tả** | Faker + business rules sinh data theo scale tier |
| **Priority** | P0 |

---

## 2.5 Analytics

### FR-AN-01 — SQL Analytics Catalog

| | |
|--|--|
| **Mô tả** | Thư viện ≥ 100 câu SQL theo nhóm Basic/Intermediate/Advanced/Reporting |
| **Priority** | P0 |

### FR-AN-02 — Python Analytics

| | |
|--|--|
| **Mô tả** | pandas/numpy: aggregation, RFM, ABC, cohort, trend, descriptive stats |
| **Priority** | P0 |

### FR-AN-03 — Metric definitions service

| | |
|--|--|
| **Mô tả** | Single place định nghĩa Revenue, Profit, Margin, AOV… tránh mỗi module tính khác nhau |
| **Priority** | P0 |

---

## 2.6 Dashboard (Streamlit)

### FR-DB-01 — KPI Cards

| | |
|--|--|
| **Mô tả** | Revenue, Profit, Gross Margin %, Orders, Customers, Products sold, AOV |
| **Priority** | P0 |

### FR-DB-02 — Charts

| | |
|--|--|
| **Mô tả** | Line, Bar, Pie, Area, Scatter, Histogram, Heatmap, Treemap (tối thiểu 1 chart/loại trong roadmap) |
| **Priority** | P0 |

### FR-DB-03 — Filters

| | |
|--|--|
| **Mô tả** | Date range, Store, Region, Category, Employee, Customer (search/select) |
| **Priority** | P0 |

### FR-DB-04 — Multi-page layout

| | |
|--|--|
| **Mô tả** | Overview | Sales | Products | Customers | Inventory | Employees (có thể gộp) |
| **Priority** | P1 |

### FR-DB-05 — Data table / search

| | |
|--|--|
| **Mô tả** | Bảng orders/products/customers có sort, search keyword |
| **Priority** | P1 |

---

## 2.7 Reporting & Export

### FR-RP-01 — Daily Report

Tóm tắt doanh số ngày: revenue, orders, top products, payment mix.

### FR-RP-02 — Weekly Report

So sánh 7 ngày, trend, store ranking.

### FR-RP-03 — Monthly Report

Đầy đủ KPI + category/region + MoM.

### FR-RP-04 — Quarterly Report

QoQ, top performers, RFM snapshot.

### FR-RP-05 — Yearly Report

YoY, seasonal pattern, executive summary.

### FR-RP-06 — Export Excel

| | |
|--|--|
| **Mô tả** | Multi-sheet workbook (Summary, Details, Charts data) qua openpyxl |
| **Priority** | P0 |

### FR-RP-07 — Export PDF

| | |
|--|--|
| **Mô tả** | Executive PDF (cover, KPI, tables, simple charts images) qua reportlab + matplotlib |
| **Priority** | P0 |

### FR-RP-08 — CLI report generation

| | |
|--|--|
| **Mô tả** | `typer` command: `report generate --type monthly --format both` |
| **Priority** | P0 |

---

## 2.8 Search & Filter (cross-cutting)

### FR-SF-01 — Bộ lọc dữ liệu

Áp dụng thống nhất trên dashboard và một phần report params: date, store, region, category, brand, employee, customer, order status.

### FR-SF-02 — Tìm kiếm

- Customer: name/email/phone  
- Product: sku/name  
- Order: order_number  
Triển khai SQL `ILIKE` / full prefix index khi cần.

---

## 2.9 System / Ops functions

### FR-SYS-01 — Configuration

Load từ `.env` + pydantic-settings (DB URL, log level, currency, default date range).

### FR-SYS-02 — Logging

loguru: file + console; stages ETL, errors, metrics.

### FR-SYS-03 — Database migrations

Alembic upgrade/downgrade.

### FR-SYS-04 — Health check CLI

`db ping`, `db stats` (row counts).

---

## 2.10 Ma trận ưu tiên triển khai

| Phase gợi ý | FR chính |
|-------------|----------|
| Phase 1–2 | Docs, schema, constraints |
| Phase 3 | Seed, FR-ETL-06 |
| Phase 4 | FR-AN-01 SQL catalog |
| Phase 5 | FR-ETL-01…05 |
| Phase 6 | FR-AN-02, FR-AN-03 |
| Phase 7–8 | FR-DB-* visualization + dashboard |
| Phase 9 | FR-RP-* |
| Phase 10 | Tests cho các FR P0 |

---

## 2.11 Những gì KHÔNG là chức năng

- Đăng nhập multi-user / RBAC phức tạp (có thể mock “role” select trên Streamlit — P2)
- API REST public
- Real-time websocket updates
- Mobile native app
