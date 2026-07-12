# 1. Business Requirements

## 1.1 Bài toán doanh nghiệp

### Bối cảnh

**RetailCo** (tên giả) là chuỗi bán lẻ đa cửa hàng, kinh doanh hàng tiêu dùng, điện tử nhỏ, phụ kiện và sản phẩm theo mùa. Doanh nghiệp có:

- Nhiều **cửa hàng** (stores) tại các **vùng địa lý** (regions)
- **Nhân viên** bán hàng và quản lý cửa hàng
- **Nhà cung cấp** (suppliers) cung cấp sản phẩm theo **thương hiệu** (brands) và **danh mục** (categories)
- **Khách hàng** mua qua đơn hàng (orders) với nhiều dòng hàng (order_items)
- **Thanh toán** đa phương thức, **khuyến mãi**, **tồn kho**, **đổi trả**

Dữ liệu phát sinh từ POS, file export ERP, và một số nguồn thủ công (CSV/Excel/JSON). Hiện tại, báo cáo chủ yếu làm bằng Excel ad-hoc, thiếu chuẩn hóa, khó đối soát và không có dashboard thống nhất.

### Vấn đề cốt lõi

| Vấn đề | Hệ quả |
|--------|--------|
| Dữ liệu rời rạc, format không đồng nhất | Không tin cậy số liệu doanh thu |
| Không có single source of truth | Mỗi phòng ban “có số riêng” |
| Báo cáo thủ công, chậm | Quyết định trễ, mất cơ hội |
| Không phân tích sâu (RFM, cohort, ABC) | Không tối ưu khách hàng & tồn kho |
| Không theo dõi margin / profit rõ ràng | Bán nhiều nhưng lãi ít |
| Thiếu drill-down theo store/region/employee | Không quản lý hiệu suất vận hành |

### Bài toán cần giải

Xây dựng **Sales Analytics Dashboard** — hệ thống thu thập, làm sạch, lưu trữ, phân tích và trực quan hóa dữ liệu bán hàng — để:

1. Có **data warehouse/analytics DB** chuẩn hóa trên PostgreSQL
2. Chạy **ETL/ELT** tái sử dụng được từ file nguồn
3. Trả lời câu hỏi kinh doanh bằng **SQL + Python analytics**
4. Hiển thị **dashboard tương tác** và **xuất báo cáo Excel/PDF**

---

## 1.2 Mục tiêu hệ thống

### Mục tiêu nghiệp vụ (Business Goals)

| ID | Mục tiêu | Chỉ số thành công (ví dụ) |
|----|----------|---------------------------|
| BG-01 | Theo dõi doanh thu, lợi nhuận, biên lãi theo thời gian | KPI cards cập nhật theo filter |
| BG-02 | Xếp hạng sản phẩm, khách hàng, cửa hàng, nhân viên | Top-N, Pareto 80/20 |
| BG-03 | Phân khúc khách hàng (RFM, CLV, repeat rate) | RFM segments có thể export |
| BG-04 | Phân tích tồn kho & chuyển động kho | Cảnh báo tồn thấp / chậm luân chuyển |
| BG-05 | Đánh giá hiệu quả khuyến mãi | So sánh doanh số có/không promo |
| BG-06 | Báo cáo định kỳ (ngày/tuần/tháng/quý/năm) | File Excel + PDF đúng template |
| BG-07 | Làm sạch & chuẩn hóa dữ liệu nguồn | Tỷ lệ record reject được log |

### Mục tiêu kỹ thuật / học tập (Learning Goals)

- Thành thạo **SQL** từ cơ bản đến advanced (window, CTE, reporting)
- Thực hành **ETL**: extract multi-format → validate → clean → load
- Thiết kế **schema 3NF** + index + constraint tốt
- Viết Python **modular** (config, repo, service, analytics)
- Xây **Streamlit dashboard** + export report
- Áp dụng **testing** và **code quality** (pytest, ruff, black, mypy)

### Phạm vi (In Scope)

- Bán lẻ offline multi-store (mô phỏng)
- Dữ liệu master + transaction + inventory + returns + promotions
- Analytics SQL/Python, dashboard Streamlit, report Excel/PDF
- Seed data đa quy mô (100 → 1M records)
- CLI Typer cho ETL, seed, report, analytics

### Ngoài phạm vi (Out of Scope)

- Real-time streaming, message queue, job scheduler phân tán
- Web API (FastAPI/Django/Flask) và SPA frontend
- Auth phức tạp / multi-tenant SaaS
- Docker/K8s/CI/CD
- Thanh toán cổng thật, tích hợp ERP thật

---

## 1.3 Người sử dụng (Personas)

### P1 — Business Owner / CEO

- **Nhu cầu**: nhìn tổng quan doanh thu, profit, tăng trưởng YoY/MoM
- **Hành vi**: mở dashboard 1–2 lần/ngày, filter theo tháng/quý
- **Đau điểm**: số liệu mâu thuẫn giữa các file Excel

### P2 — Sales Manager

- **Nhu cầu**: hiệu suất cửa hàng, nhân viên, top sản phẩm
- **Hành vi**: drill-down theo region/store/employee
- **Đau điểm**: không biết ai underperform, sản phẩm nào đang “hot”

### P3 — Data Analyst

- **Nhu cầu**: SQL ad-hoc, RFM, cohort, ABC, export raw
- **Hành vi**: chạy query, notebook/pandas, xuất báo cáo
- **Đau điểm**: dữ liệu bẩn, thiếu calendar dimension, join khó

### P4 — Inventory / Operations

- **Nhu cầu**: tồn kho, stock movements, returns rate
- **Hành vi**: filter category/store, xem slow movers
- **Đau điểm**: stock-out và overstock không được cảnh báo sớm

### P5 — Developer / Learner (bạn)

- **Nhu cầu**: codebase sạch, docs rõ, roadmap phase-by-phase
- **Hành vi**: implement theo phase, viết test, demo portfolio
- **Đau điểm**: scope creep, thiếu design trước khi code

---

## 1.4 Quy trình nghiệp vụ (Business Process)

### 1.4.1 Master Data

```
Supplier → Brand/Category → Product → Assign to Store inventory
Regions → Stores → Employees (assign to store)
Customers (register / walk-in)
```

### 1.4.2 Bán hàng (Order lifecycle)

```
1. Khách chọn sản phẩm tại cửa hàng
2. Nhân viên tạo Order (draft)
3. Thêm Order Items (product, qty, unit price, discount)
4. Áp dụng Promotion (nếu có)
5. Tính subtotal, tax, discount, grand total
6. Payment (1 hoặc nhiều lần / partial — thiết kế hỗ trợ multi-payment)
7. Order status: pending → paid → completed | cancelled
8. Giảm tồn kho (stock_movements: sale_out)
9. (Tùy chọn) Return → restock / write-off
```

### 1.4.3 Tồn kho

```
Purchase / Transfer In  → stock_movements (+) → inventory.quantity
Sale                    → stock_movements (-) → inventory.quantity
Return restock          → stock_movements (+) → inventory.quantity
Adjustment / Damage     → stock_movements (±) → inventory.quantity
```

### 1.4.4 Analytics & Reporting

```
Raw files / seed / operational tables
        → ETL clean load
        → SQL metrics & reporting queries
        → Python analytics (RFM, cohort…)
        → Dashboard filters + charts
        → Scheduled/manual Excel & PDF export
```

---

## 1.5 Vấn đề doanh nghiệp đang gặp (As-Is)

1. **Data silos**: mỗi cửa hàng export file riêng, cột không thống nhất.
2. **Không có dimension thời gian chuẩn**: so sánh YoY/QoQ khó.
3. **Không tính profit chuẩn**: thiếu cost hoặc cost không đồng bộ product.
4. **Khách hàng không được phân khúc**: marketing “bắn đại”.
5. **Tồn kho mù**: bán hết vẫn nhận order, hoặc ứ hàng theo mùa.
6. **Báo cáo trễ**: cuối tháng mới tổng hợp, sai sót do copy-paste.
7. **Không audit trail**: không biết ai sửa file, khi nào load fail.

---

## 1.6 Dashboard sẽ giải quyết điều gì (To-Be)

| Nhu cầu | Giải pháp hệ thống |
|---------|-------------------|
| Một nguồn số liệu thống nhất | PostgreSQL schema chuẩn + ETL validate |
| Nhìn nhanh sức khỏe kinh doanh | KPI cards: Revenue, Profit, Orders, Customers, AOV |
| Hiểu xu hướng | Line/Area chart theo ngày/tuần/tháng |
| So sánh kênh/cửa hàng/vùng | Bar, Heatmap, filter region/store |
| Ưu tiên sản phẩm & khách | Top-N, Treemap category, Pareto, ABC |
| Quản trị hiệu suất nhân viên | Ranking employees by revenue/orders |
| Phân khúc & giữ chân KH | RFM, CLV, Repeat Rate, Cohort |
| Báo cáo định kỳ | Excel multi-sheet + PDF executive summary |
| Học & portfolio | 100+ SQL, modular Python, full docs |

### Câu hỏi kinh doanh hệ thống phải trả lời được

1. Doanh thu / lợi nhuận hôm nay, tuần này, tháng này so với kỳ trước?
2. Top 10 sản phẩm, danh mục, thương hiệu theo doanh thu và margin?
3. Cửa hàng / vùng nào tăng trưởng, cửa hàng nào tụt?
4. Nhân viên bán hàng xuất sắc nhất theo quý?
5. Khách hàng VIP (RFM), khách churn risk?
6. AOV, conversion proxy (orders/customers active), CLV?
7. Promotion có thực sự tăng doanh số hay chỉ “ăn margin”?
8. Sản phẩm nào slow-moving / sắp hết hàng?
9. Tỷ lệ đổi trả theo category/store?
10. Phân bố 80/20: bao nhiêu % sản phẩm tạo 80% doanh thu?

---

## 1.7 Giả định & ràng buộc

### Giả định

- Tiền tệ mặc định: **VND** (có thể config; seed dùng VND hoặc USD thống nhất — chốt **VND**).
- Một đơn hàng thuộc **một cửa hàng** và **một nhân viên** chính.
- Giá bán tại thời điểm order được **snapshot** vào `order_items` (không phụ thuộc giá hiện tại product).
- Cost để tính profit lấy từ `order_items.unit_cost` (snapshot) hoặc fallback `products.cost_price`.
- Soft delete (`deleted_at`) cho master data; transaction lịch sử giữ hard history, hủy bằng status.

### Ràng buộc kỹ thuật

- Chạy local PostgreSQL (không Docker trong phạm vi dự án).
- Single-process ETL/CLI; không queue.
- Streamlit single-user / demo multi-filter, không SSO.

---

## 1.8 Thành công của dự án (Definition of Done — cấp portfolio)

- [ ] Schema 3NF đầy đủ 16 bảng (+ calendar), migration Alembic
- [ ] Seed data các mức 100 / 1K / 10K / 100K / 1M (có script chọn scale)
- [ ] ≥ 100 SQL exercises có file/query catalog
- [ ] ETL CSV/Excel/JSON → PostgreSQL với validation + logging
- [ ] Analytics Python (pandas) cho RFM, ABC, cohort tối thiểu
- [ ] Streamlit dashboard có KPI + ≥ 6 loại chart + multi-filter
- [ ] Export Daily/Weekly/Monthly Excel + PDF
- [ ] pytest + ruff/black/mypy pass trên core
- [ ] Docs đầy đủ trong `docs/`

---

## 1.9 Thuật ngữ (Glossary)

| Thuật ngữ | Định nghĩa |
|-----------|------------|
| Revenue (Doanh thu) | Tổng `line_total` (sau discount dòng) của order completed/paid, trừ returns nếu policy net |
| Gross Profit | Revenue − COGS (cost of goods sold) |
| Gross Margin % | Gross Profit / Revenue × 100 |
| AOV | Average Order Value = Revenue / số orders |
| CLV | Customer Lifetime Value — tổng net revenue theo khách (và biến thể dự báo đơn giản) |
| RFM | Recency, Frequency, Monetary |
| ABC Analysis | Phân loại SKU A/B/C theo đóng góp doanh thu (Pareto) |
| Cohort | Nhóm khách theo tháng đăng ký/mua đầu, theo dõi retention |
| Soft delete | `deleted_at IS NOT NULL` thay vì xóa vật lý |
| Snapshot price | Giá/cost lưu trên order_item tại thời điểm bán |

---

## 1.10 Mapping Personas → Modules

| Persona | Module chính |
|---------|----------------|
| CEO | Dashboard KPI, Yearly/Monthly report PDF |
| Sales Manager | Dashboard filters store/employee, ranking SQL |
| Analyst | SQL scripts, analytics services, Excel export raw |
| Ops | Inventory views, stock movements, returns rate |
| Developer | Toàn bộ codebase, tests, docs |
