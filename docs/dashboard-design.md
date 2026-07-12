# 9. Dashboard Design (Streamlit)

## 9.1 Mục tiêu UX

- **5 giây đầu:** CEO thấy sức khỏe kinh doanh (KPI)  
- **30 giây:** Sales Manager filter store/region và so sánh  
- **2 phút:** Analyst drill charts + table  
- Giao diện sạch, không quá nhiều widget một trang  

---

## 9.2 Cấu trúc multipage

```text
Home / Overview
Sales Analysis
Products
Customers
Inventory & Returns
Employees (optional gộp Sales)
About / Data Dictionary (optional)
```

Entry: `streamlit run app/dashboard/app.py`

---

## 9.3 Layout tổng thể (mọi page)

```text
┌──────────────────────────────────────────────────────────┐
│  Title: Sales Analytics Dashboard          [Last refresh]│
├────────────┬─────────────────────────────────────────────┤
│ SIDEBAR    │  MAIN                                       │
│            │                                             │
│ Date range │  Row 1: KPI Cards (4–7 metrics)             │
│ Region     │                                             │
│ Store      │  Row 2: Primary trend chart (wide)          │
│ Category   │                                             │
│ Employee   │  Row 3: 2-column secondary charts           │
│ Customer   │                                             │
│ Status     │  Row 4: Detail table / rankings             │
│            │                                             │
│ [Apply]    │                                             │
│ [Reset]    │                                             │
└────────────┴─────────────────────────────────────────────┘
```

**Streamlit notes:**

- Filters trong `st.sidebar`  
- KPI dùng `st.metric` (delta MoM nếu có)  
- Charts: `st.plotly_chart(..., use_container_width=True)`  
- Cache: `@st.cache_data(ttl=300)` trên hàm load theo filter hash  

---

## 9.4 Global filters

| Filter | Control | Default | Notes |
|--------|---------|---------|-------|
| Date range | `st.date_input` | Last 30 days | map → AnalyticsFilter |
| Region | multiselect | All | cascades store list |
| Store | multiselect | All | |
| Category | multiselect | All | |
| Employee | multiselect / search | All | |
| Customer | selectbox search | None (all) | optional |
| Order status | multiselect | paid, completed | advanced expander |

**Cascading:** đổi Region → reload Store options (query distinct).  
**Apply pattern:** dùng `st.form` để tránh rerun mỗi widget (khuyến nghị).

---

## 9.5 Page: Overview

### KPI Cards (Row 1)

| KPI | Source metric | Delta |
|-----|---------------|-------|
| Revenue | MetricsService.revenue | vs previous period same length |
| Gross Profit | .profit | |
| Gross Margin % | .margin_pct | |
| Orders | .order_count | |
| Customers (buyers) | .buyer_count | |
| AOV | .aov | |
| Products sold (units) | .units_sold | optional 7th |

### Charts

| Chart | Type | Data |
|-------|------|------|
| Revenue over time | Line / Area | daily or weekly series |
| Revenue by region | Bar | R11 |
| Category mix | Pie or Treemap | R09 |
| Top 10 products | Horizontal bar | R04 |

### Table

- Top 10 stores summary  

---

## 9.6 Page: Sales

| Section | Chart | |
|---------|-------|--|
| Trend | Line multi-series (this year vs last) | |
| Heatmap | Month × Weekday revenue | calendar |
| Scatter | Order total vs item count | anomaly feel |
| Histogram | Distribution of order totals | |
| Payment mix | Pie | R28 |
| Store ranking | Bar | R08 |

Filters đặc thù: group-by grain (day/week/month).

---

## 9.7 Page: Products

| Section | Visualization |
|---------|----------------|
| Top by revenue / profit toggle | Bar |
| Category treemap | Treemap |
| ABC classes | Pie + table |
| Margin by brand | Bar |
| Slow movers | Table (high stock low sales) |

---

## 9.8 Page: Customers

| Section | Visualization |
|---------|----------------|
| RFM segment counts | Bar |
| CLV top customers | Bar/table |
| Repeat rate KPI | metric |
| Cohort retention | Heatmap |
| New vs returning | Stacked area |

---

## 9.9 Page: Inventory & Returns

| Section | Visualization |
|---------|----------------|
| Low stock count KPI | metric |
| Stock by category | Bar |
| Movements over time | Line |
| Return rate by category | Bar |
| Returns reasons | Pie |

---

## 9.10 Page: Employees (optional)

| Section | Visualization |
|---------|----------------|
| Top employees revenue | Bar |
| Orders per employee | Bar |
| Scatter revenue vs orders | Scatter |

---

## 9.11 Components design

### `components/filters.py`

- `render_sidebar_filters() -> AnalyticsFilter`

### `components/kpi_cards.py`

- `render_kpi_row(summary: KPIResult)`

### `components/charts.py`

- Thin wrappers gọi `app.visualization.plotly_charts`

### `state.py`

- Keys session: `filters`, `last_query_at`

---

## 9.12 Empty & error states

| State | UI |
|-------|-----|
| No data in range | `st.info("Không có đơn hàng trong kỳ đã chọn")` |
| DB connection fail | `st.error` + log |
| Partial dimension missing | hide chart + warning |

---

## 9.13 Performance UX

1. Form submit filters  
2. cache_data by filter tuple  
3. Limit default top-N = 10/20  
4. Aggregate in SQL, không pull all order_items lên browser logic  

---

## 9.14 Theming

- Streamlit theme config `.streamlit/config.toml` (optional): primary color professional blue/teal  
- Plotly template thống nhất `plotly_white` + brand colors trong `styles.py`  
- Currency format: `₫` / VND với separator  

---

## 9.15 Accessibility & polish (P2)

- Chart titles rõ  
- Axis labels có đơn vị  
- Tooltip có format số  
- Caption nguồn: "Data: PostgreSQL sales DB"  

---

## 9.16 Mapping FR

| FR | Implementation |
|----|----------------|
| FR-DB-01 | Overview KPI row |
| FR-DB-02 | charts across pages |
| FR-DB-03 | sidebar filters |
| FR-DB-04 | multipage |
| FR-DB-05 | dataframes `st.dataframe` |

---

## 9.17 Checklist Dashboard phase

- [ ] Multipage structure  
- [ ] Global filters form  
- [ ] ≥ 7 KPI metrics  
- [ ] All 8 chart types xuất hiện ≥ 1 lần  
- [ ] cache_data  
- [ ] empty states  
- [ ] uses MetricsService only for KPIs  
