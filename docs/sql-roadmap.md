# 5. SQL Learning & Implementation Roadmap

> **Nguyên tắc:** Giai đoạn thiết kế **không viết SQL đầy đủ**.  
> Tài liệu này là **catalog ≥ 100 bài toán** sẽ implement trong Phase 4 (và dùng lại ở Dashboard/Reporting).

## 5.1 Mục tiêu

- Luyện SQL từ cơ bản → nâng cao trên schema Sales Analytics
- Mỗi query có: **ID, tên, mục tiêu học, bảng liên quan, độ khó, output kỳ vọng**
- File triển khai gợi ý: `sql/basic/`, `sql/intermediate/`, `sql/advanced/`, `sql/reporting/`, `sql/optimization/`
- Catalog index: `sql/README.md` (khi code)

### Quy ước metric (áp dụng mọi reporting query)

| Metric | Định nghĩa chuẩn |
|--------|------------------|
| Revenue | `SUM(order_items.line_total)` join orders `status IN ('paid','completed')` |
| COGS | `SUM(quantity * unit_cost)` cùng filter |
| Gross Profit | Revenue − COGS |
| Gross Margin % | Profit / NULLIF(Revenue,0) |
| Orders count | `COUNT(DISTINCT orders.id)` với status trên |
| AOV | Revenue / Orders count |

*(Có thể net returns ở nhóm Reporting nâng cao — ghi chú riêng từng bài.)*

---

## 5.2 Basic SQL (B01–B25) — 25 queries

| ID | Tên bài toán | Kỹ năng | Mô tả |
|----|--------------|---------|-------|
| B01 | List all active products | SELECT | Lấy id, sku, name, unit_price sản phẩm active |
| B02 | Customers in a city | WHERE | Lọc customers theo city |
| B03 | Orders on a date | WHERE date | Orders trong một ngày cụ thể |
| B04 | High value orders | WHERE + comparison | total_amount > ngưỡng |
| B05 | Sort products by price | ORDER BY | Giá giảm dần |
| B06 | Top 10 expensive products | ORDER BY + LIMIT | |
| B07 | Distinct payment methods | DISTINCT | Các method đã dùng |
| B08 | Distinct cities of customers | DISTINCT | |
| B09 | Search product by name | LIKE | `ILIKE '%keyword%'` |
| B10 | Search customer email domain | LIKE | `%@gmail.com` |
| B11 | Orders in date range | BETWEEN | order_date BETWEEN |
| B12 | Products price band | BETWEEN | unit_price trong khoảng |
| B13 | Orders of selected stores | IN | store_id IN (...) |
| B14 | Orders by status set | IN | status IN ('paid','completed') |
| B15 | Null email customers | IS NULL | |
| B16 | Non-null phone customers | IS NOT NULL | |
| B17 | Column aliases | AS | Đặt alias tiếng Anh rõ nghĩa |
| B18 | Computed line preview | arithmetic | quantity * unit_price |
| B19 | String concat names | \|\| / CONCAT | full_name employees |
| B20 | Date parts extract | EXTRACT | year/month từ order_date |
| B21 | Boolean filter stores | WHERE boolean | is_active = TRUE |
| B22 | Exclude cancelled | WHERE NOT / <> | |
| B23 | Pagination pattern | LIMIT OFFSET | page 2 size 20 |
| B24 | Order by multiple columns | ORDER BY a,b | status, order_date |
| B25 | Case-insensitive code lookup | WHERE UPPER/LOWER | |

**Deliverable Phase 4:** 25 file `.sql` + expected row shape notes.

---

## 5.3 Intermediate SQL (I01–I30) — 30 queries

| ID | Tên bài toán | Kỹ năng | Mô tả |
|----|--------------|---------|-------|
| I01 | Orders with customer names | INNER JOIN | orders ⋈ customers |
| I02 | Order lines with product | INNER JOIN | order_items ⋈ products |
| I03 | Orders with store & region | multi JOIN | orders→stores→regions |
| I04 | Products with category & brand | multi JOIN | |
| I05 | Employees with store | INNER JOIN | |
| I06 | Orders without payments yet | LEFT JOIN anti | payments NULL |
| I07 | Products never sold | LEFT JOIN anti | |
| I08 | Customers with no orders | LEFT JOIN anti | |
| I09 | Stores without employees | LEFT JOIN anti | |
| I10 | All products and stock | LEFT JOIN inventory | |
| I11 | RIGHT JOIN demo | RIGHT JOIN | (cửa hàng ← inventory) minh họa |
| I12 | FULL JOIN demo | FULL JOIN | so khớp 2 tập mã (staging vs dim) |
| I13 | Revenue by order | GROUP BY | sum line_total per order_id |
| I14 | Revenue by store | GROUP BY | |
| I15 | Revenue by category | GROUP BY | |
| I16 | Orders count by status | GROUP BY | |
| I17 | Avg order value by store | GROUP BY + AVG | |
| I18 | Stores with revenue > X | HAVING | |
| I19 | Categories with > N products | HAVING | |
| I20 | Customers with ≥ 3 orders | HAVING | |
| I21 | Payment method mix | GROUP BY method | count/sum |
| I22 | CASE status label | CASE WHEN | map status → label |
| I23 | CASE price tier | CASE WHEN | budget/mid/premium |
| I24 | CASE region performance | CASE WHEN + aggregate | |
| I25 | Subquery: products above avg price | scalar subquery | |
| I26 | Subquery: orders above avg total | |
| I27 | IN subquery top categories | |
| I28 | EXISTS active promo orders | EXISTS | |
| I29 | Correlated: customer last order date | correlated subquery | |
| I30 | Derived table monthly revenue | FROM (subquery) | |

---

## 5.4 Advanced SQL (A01–A35) — 35 queries

### CTE & Recursive

| ID | Tên | Kỹ năng | Mô tả |
|----|-----|---------|-------|
| A01 | Monthly revenue CTE | CTE | WITH monthly AS (...) |
| A02 | Multi-CTE profit report | multiple CTE | revenue + cogs + profit |
| A03 | Filter CTE then join | CTE hygiene | |
| A04 | Category tree recursive | Recursive CTE | parent_id walk |
| A05 | Employee hierarchy | Recursive CTE | manager chain |
| A06 | Region hierarchy path | Recursive CTE | path materialize |
| A07 | Bill of depth levels | Recursive + level | |

### Window — ranking

| ID | Tên | Kỹ năng | Mô tả |
|----|-----|---------|-------|
| A08 | Row number all products by price | ROW_NUMBER | |
| A09 | Top product per category | ROW_NUMBER + PARTITION | rn=1 |
| A10 | Rank stores by revenue | RANK | ties |
| A11 | Dense rank employees | DENSE_RANK | |
| A12 | NTILE customer quartiles | NTILE(4) | monetary |
| A13 | Top 3 products per store | PARTITION store | |
| A14 | Rank within month | PARTITION year,month | |

### Window — value & lag/lead

| ID | Tên | Kỹ năng | Mô tả |
|----|-----|---------|-------|
| A15 | Running total revenue | SUM OVER ORDER BY date | |
| A16 | Running total per store | SUM + PARTITION store | |
| A17 | Moving avg 7-day revenue | AVG frame | ROWS 6 PRECEDING |
| A18 | MoM revenue change | LAG | |
| A19 | Next month revenue | LEAD | |
| A20 | YoY using LAG 12 | LAG | monthly series |
| A21 | First order date per customer | FIRST_VALUE | |
| A22 | Last order date per customer | LAST_VALUE / MAX | frame đúng |
| A23 | Percent of total revenue | SUM / SUM OVER() | |
| A24 | Cumulative distribution | CUME_DIST | |
| A25 | Percent rank products | PERCENT_RANK | |

### Window + business

| ID | Tên | Kỹ năng | Mô tả |
|----|-----|---------|-------|
| A26 | Repeat purchase flag | LAG order_date per customer | |
| A27 | Days between orders | LAG diff | |
| A28 | Session-like order sequence | ROW_NUMBER per customer | |
| A29 | Best selling day of week | window + calendar | |
| A30 | Contribution margin rank | profit window | |
| A31 | Inventory vs sales velocity | multi CTE + window | |
| A32 | Promo vs non-promo AOV | CASE + window optional | |
| A33 | Return rate by product | CTE returns/sales | |
| A34 | Payment completion lag | paid_at - order_date | |
| A35 | Deduplicate keep latest | ROW_NUMBER quality | |

---

## 5.5 Reporting SQL (R01–R30) — 30 queries

| ID | Báo cáo | Mô tả output |
|----|---------|--------------|
| R01 | Revenue overall | total revenue kỳ |
| R02 | Profit overall | gross profit + margin |
| R03 | Gross margin by category | table category, rev, cogs, margin |
| R04 | Top products by revenue | Top 20 |
| R05 | Top products by profit | Top 20 |
| R06 | Top customers by revenue | Top 20 + order count |
| R07 | Top employees by revenue | |
| R08 | Top stores by revenue | |
| R09 | Sales by category | bar-ready |
| R10 | Sales by brand | |
| R11 | Sales by region | |
| R12 | Sales by store | |
| R13 | Sales by month | time series |
| R14 | Sales by quarter | |
| R15 | Sales by year | |
| R16 | Sales by day of week | calendar join |
| R17 | Average Order Value overall | |
| R18 | AOV by store / channel | |
| R19 | Customer Lifetime Value | sum net revenue per customer |
| R20 | Repeat Customer Rate | customers ≥2 orders / total buyers |
| R21 | ABC Analysis products | A≤80%, B≤95%, C rest cumulative |
| R22 | Pareto 80/20 validation | count products for 80% rev |
| R23 | RFM raw scores | recency days, frequency, monetary |
| R24 | RFM segments | map scores → Champion/Loyal/AtRisk… |
| R25 | Cohort by first order month | retention matrix skeleton |
| R26 | Sales trend with MoM % | series + pct_change |
| R27 | New vs returning customers | monthly |
| R28 | Payment method share | % of amount |
| R29 | Returns rate by category | returned_qty / sold_qty |
| R30 | Net revenue after returns | revenue − refunds |

**Ghi chú RFM/Cohort:** có thể implement SQL-first; Python analytics tinh chỉnh segment labels.

---

## 5.6 SQL Optimization lab (O01–O15) — 15 exercises

| ID | Chủ đề | Việc làm |
|----|--------|----------|
| O01 | Read EXPLAIN | Chạy EXPLAIN trên I14 |
| O02 | EXPLAIN ANALYZE | So sánh trước/sau index |
| O03 | Seq scan vs index scan | Tạo case filter selective |
| O04 | Index on order_date | Measure |
| O05 | Composite (store_id, order_date) | Dashboard pattern |
| O06 | Composite (status, order_date) | |
| O07 | Index order_items(product_id) | Top products |
| O08 | Covering index concept | INCLUDE columns (PG11+) |
| O09 | Avoid SELECT * | Rewrite |
| O10 | SARGability | Không wrap column trong hàm khi filter |
| O11 | Join order awareness | Large fact first filters |
| O12 | CTE materialization notes | PG15+ behavior awareness |
| O13 | Partial index low stock | inventory |
| O14 | Analyze / vacuum awareness | Document ops checklist |
| O15 | Query rewrite HAVING vs subquery | equivalent plans |

**Deliverable:** `sql/optimization/notes.md` ghi before/after timing (máy local).

---

## 5.7 Tổng số bài toán

| Nhóm | Số lượng |
|------|----------|
| Basic | 25 |
| Intermediate | 30 |
| Advanced | 35 |
| Reporting | 30 |
| Optimization | 15 |
| **Tổng** | **135** |

> Vượt yêu cầu 100 để có buffer khi gộp/bỏ bài trùng.

---

## 5.8 Thứ tự học / triển khai đề xuất

```text
Week-ish 1: B01–B25 + verify seed data
Week-ish 2: I01–I30 joins & group
Week-ish 3: A01–A17 CTE + windows core
Week-ish 4: A18–A35 + R01–R15
Week-ish 5: R16–R30 RFM/ABC/Cohort
Week-ish 6: O01–O15 index lab
```

Song song: mỗi reporting query map vào dashboard chart/KPI (xem `dashboard-design.md`).

---

## 5.9 Chuẩn file khi implement

```text
sql/
  README.md                 # catalog table
  basic/B01_list_products.sql
  intermediate/I01_orders_customers.sql
  advanced/A09_top_product_per_category.sql
  reporting/R23_rfm_raw.sql
  optimization/O05_composite_store_date.sql
  _expected/                # optional notes or sample outputs
```

Header mỗi file:

```text
-- ID: R04
-- Title: Top products by revenue
-- Skills: JOIN, GROUP BY, ORDER BY, LIMIT
-- Tables: order_items, products, orders
-- Params: :start_date, :end_date (documented)
```

---

## 5.10 Mapping Reporting → Dashboard / Excel

| Report SQL | Dashboard widget | Excel sheet |
|------------|------------------|-------------|
| R01–R02 | KPI cards | Summary |
| R13–R15 | Line/Area | Trend |
| R04–R08 | Bar | Rankings |
| R09–R11 | Pie/Treemap | Breakdown |
| R21–R24 | Tables + bar | RFM_ABC |
| R25 | Heatmap | Cohort |
| R26 | Line dual axis | Trend |

---

## 5.11 Checklist hoàn thành SQL phase

- [x] 135 files trong `sql/`
- [x] Catalog README (`sql/README.md`)
- [x] Metric definitions thống nhất (`sql/metrics.md`)
- [x] Reporting queries param-ready (date filters documented)
- [x] Optimization notes (`sql/optimization/notes.md`)
- [x] CLI runner: `sales-dashboard sql list|show|run`
