# 11. Reporting Design

## 11.1 Mục tiêu

Sinh báo cáo định kỳ phục vụ CEO/Sales Manager, **tái sử dụng MetricsService + reporting SQL**, xuất **Excel** (openpyxl) và **PDF** (reportlab + matplotlib images).

CLI:

```text
report generate --type daily|weekly|monthly|quarterly|yearly \
                --format excel|pdf|both \
                --date YYYY-MM-DD \
                --store-id optional
```

Output:

```text
output/reports/excel/monthly_2024_06.xlsx
output/reports/pdf/monthly_2024_06.pdf
```

---

## 11.2 Period resolution

| Type | Period definition | Comparison period |
|------|-------------------|-------------------|
| Daily | calendar day D | D-1 |
| Weekly | ISO week containing D (Mon–Sun) | previous ISO week |
| Monthly | month of D | previous month |
| Quarterly | quarter of D | previous quarter |
| Yearly | year of D | previous year |

Mọi report nhận `as_of_date` (default today).

---

## 11.3 Common structure (mọi report)

1. **Cover / Header:** title, period label, generated_at, filters  
2. **Executive KPI summary**  
3. **Trend section** (grain phụ thuộc type)  
4. **Rankings:** products, stores, employees, customers (depth tùy type)  
5. **Breakdowns:** category, region, payment  
6. **Quality / ops (optional):** returns rate, low stock snapshot  
7. **Appendix:** definitions of metrics  

---

## 11.4 Daily Report

### Mục đích

Họp đầu ngày / ca: “Hôm qua (hoặc ngày D) bán được gì?”

### Nội dung

| Section | Chi tiết |
|---------|----------|
| KPI | Revenue, Profit, Margin, Orders, AOV, Units, Buyers |
| vs yesterday | deltas |
| Hourly trend (optional P2) | nếu có hour trong order_date |
| Top 10 products | revenue + qty |
| Top stores | |
| Payment mix | |
| Cancelled orders count | operational |
| Returns same day | count + refund |

### Excel sheets

1. `Summary`  
2. `TopProducts`  
3. `TopStores`  
4. `Payments`  
5. `Orders` (optional detail sample top 100)  

### PDF

2–3 pages: KPI + 2 charts (trend if multi-day context none → bar top products) + table top products.

---

## 11.5 Weekly Report

### Mục đích

Review tuần cho Sales Manager.

### Nội dung

| Section | Chi tiết |
|---------|----------|
| KPI week | + WoW delta |
| Daily trend within week | line 7 points |
| Store ranking | full |
| Employee ranking | top 15 |
| Category mix | |
| New vs returning | |
| Margin watch | categories margin < threshold |

### Excel sheets

`Summary`, `DailyTrend`, `Stores`, `Employees`, `Categories`, `Customers_Top`

### PDF

3–4 pages executive.

---

## 11.6 Monthly Report

### Mục đích

Báo cáo chính thức tháng — đầy đủ nhất cho portfolio demo.

### Nội dung

| Section | Chi tiết |
|---------|----------|
| KPI + MoM + vs same month last year (if data) | |
| Daily/weekly revenue trend | |
| Region & store performance | |
| Category & brand | |
| Top 20 products / customers | |
| ABC snapshot | |
| RFM segment distribution | |
| Repeat customer rate | |
| Returns analysis | |
| Inventory health | low stock count, top overstock |

### Excel sheets

1. Summary  
2. Trend  
3. Regions  
4. Stores  
5. Categories  
6. Products  
7. Customers  
8. RFM  
9. ABC  
10. Returns  
11. Inventory  
12. Definitions  

### PDF

5–8 pages: cover, KPI, trends, rankings, customer analytics, appendix definitions.

---

## 11.7 Quarterly Report

### Mục đích

Nhịp board / planning quý.

### Nội dung

- QoQ KPI  
- Monthly bars trong quý  
- Top performers (store, employee, product)  
- Cohort retention snapshot (3–6 months window)  
- Pareto 80/20  
- Promotion effectiveness (orders with promo vs without)  
- Strategic commentary placeholders (markdown text block empty for user)

### Excel

`Summary`, `Monthly`, `Rankings`, `Cohort`, `Pareto`, `Promos`

### PDF

Executive 6 pages max — nhấn mạnh insight tables.

---

## 11.8 Yearly Report

### Mục đích

Tổng kết năm / portfolio “annual review”.

### Nội dung

- YoY KPI  
- Monthly seasonality line  
- Quarter comparison  
- Annual top 50 products (excel) / top 20 (pdf)  
- Customer growth: new customers per month  
- RFM year-end snapshot  
- Returns rate yearly  
- Inventory turns proxy: COGS / avg inventory (simplified)

### Excel

Broad sheets + `Monthly_Detail`

### PDF

“Board pack” style 8–10 pages.

---

## 11.9 Excel technical design (openpyxl)

| Concern | Approach |
|---------|----------|
| Styles | header fill, bold, freeze panes |
| Numbers | formats `# ,##0.00` or integer VND |
| Column width | auto approx |
| Charts in Excel | optional P2; default data only + dashboard for charts |
| Multiple sheets | one builder per sheet function |
| File name | `{type}_{period_label}.xlsx` |

Builder pipeline:

```text
ReportService.collect(type, params) -> ReportDataPackage
ExcelBuilder.render(package) -> path
```

---

## 11.10 PDF technical design (reportlab)

| Concern | Approach |
|---------|----------|
| Page size | A4 |
| Fonts | built-in + optional DejaVu for Unicode VN |
| Layout | SimpleDocTemplate, Platypus paragraphs/tables/spacers |
| Charts | Matplotlib PNG in memory or temp → Image flowable |
| Header/footer | page number, confidential demo label |
| KPI | table 2×N or cards as tables |

**Unicode tiếng Việt:** chốt embed font TTF (ví dụ DejaVuSans) trong `assets/fonts/` khi implement.

---

## 11.11 ReportDataPackage (logical schema)

```text
ReportDataPackage:
  meta: type, period_start, period_end, generated_at, filters
  kpis: KPIResult current + previous + deltas
  series: list[TimePoint]
  rankings: {products, stores, employees, customers}
  breakdowns: {categories, regions, payments}
  extras: {rfm, abc, cohort, returns, inventory}  # by type
```

---

## 11.12 Metric consistency

Report **bắt buộc** dùng cùng định nghĩa với Dashboard (`MetricsService`).  
Mọi divergence là bug.

---

## 11.13 Checklist Reporting phase

- [x] 5 period types daily→yearly  
- [x] Excel multi-sheet (openpyxl)  
- [x] PDF with KPI + charts (reportlab + matplotlib)  
- [x] CLI `report generate`  
- [x] Output paths under `output/reports/`  
- [x] Definitions sheet/appendix  
- [ ] Live run + VN font embed polish (optional P2: DejaVu)  
