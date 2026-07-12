# 10. Data Visualization Design

## 10.1 Vai trò hai thư viện

| Thư viện | Khi nào dùng | Không dùng cho |
|----------|--------------|----------------|
| **Plotly** | Dashboard Streamlit tương tác: zoom, hover, legend toggle | PDF print pipeline chính |
| **Matplotlib** | Báo cáo PDF, hình static, histogram nhanh trong notebook/script | UX interactive chính trên Streamlit |

### Lý do

- Plotly tích hợp tốt `st.plotly_chart`, JSON-serializable figures, subplot linh hoạt.  
- Matplotlib + reportlab: chèn PNG/SVG vào PDF ổn định, kiểm soát dpi/size.  
- Tránh hai library vẽ cùng một chart trên dashboard (duplicate maintenance).

---

## 10.2 Nguyên tắc chọn loại biểu đồ

1. **So sánh giữa categories** → Bar  
2. **Xu hướng theo thời gian** → Line / Area  
3. **Tỷ trọng phần toàn thể** → Pie (≤ 6 slices) hoặc Treemap  
4. **Phân bố** → Histogram  
5. **Tương quan 2 biến** → Scatter  
6. **Ma trận 2 chiều categorical/time** → Heatmap  
7. **Phân cấp tỷ trọng** → Treemap  

### Anti-patterns

- Pie với > 8 slices → chuyển Bar  
- Dual axis lạm dụng → khó đọc  
- 3D charts → không dùng  
- Rainbow random colors → dùng palette cố định  

---

## 10.3 Mapping KPI / báo cáo → chart type

| Phân tích / KPI | Chart | Library chính | Ghi chú |
|-----------------|-------|---------------|---------|
| Revenue over time | Line / Area | Plotly | dual line actual vs previous period |
| MoM / YoY trend | Line | Plotly | annotate % |
| Revenue by store/region | Bar (horizontal nếu nhiều label) | Plotly | |
| Category share | Pie (ít) / Treemap (nhiều) | Plotly | |
| Brand hierarchy in category | Treemap | Plotly | |
| Top N products | Bar horizontal | Plotly | |
| Top customers | Bar | Plotly | |
| Payment method mix | Pie | Plotly | |
| Order value distribution | Histogram | Plotly + MPL for PDF | |
| AOV vs orders by store | Scatter | Plotly | size = revenue |
| Weekday × month seasonality | Heatmap | Plotly | |
| Cohort retention | Heatmap | Plotly | |
| RFM segment size | Bar | Plotly | |
| ABC class share | Pie | Plotly | |
| Profit by category | Bar stacked or grouped | Plotly | rev vs profit |
| Inventory on hand by category | Bar | Plotly | |
| Stock movements timeline | Line | Plotly | |
| Returns reasons | Pie | Plotly | |
| Employee performance | Bar / Scatter | Plotly | |
| PDF executive trend | Line small | **Matplotlib** | 120–150 dpi PNG |
| PDF ranking table visual | Barh | Matplotlib | |

---

## 10.4 Đặc tả từng loại chart trong dự án

### Line Chart

- **Dùng:** daily/weekly/monthly revenue, profit  
- **X:** time  
- **Y:** money  
- **Options:** markers off nếu dense; hover unified  

### Area Chart

- **Dùng:** revenue trend emphasis; stacked new vs returning customers  
- **Cẩn thận:** stacked area khó so sánh tuyệt đối  

### Bar Chart

- **Dùng:** rankings, comparisons  
- **Horizontal** khi tên sản phẩm dài  
- **Sorted** theo metric  

### Pie Chart

- **Dùng:** payment mix, ABC share, ≤ 6 regions  
- **Luôn** có % + legend  

### Scatter Plot

- **Dùng:** orders count vs revenue by store; qty vs margin by product  
- **Hover:** name dimension  

### Histogram

- **Dùng:** phân bố `total_amount`, AOV-like line totals  
- **Bins:** rule Freedman–Diaconis hoặc fixed 20–30  

### Heatmap

- **Dùng:** calendar heatmap (dow × week); cohort (cohort_month × period_number)  
- **Color scale:** sequential blues/greens; center mid cho diverging nếu % change  

### Treemap

- **Dùng:** category → product revenue hierarchy  
- **Values:** revenue; color: margin optional  

---

## 10.5 Design system màu

```text
Primary:    #2563EB  (blue)
Secondary:  #0D9488  (teal)
Success:    #16A34A
Warning:    #D97706
Danger:     #DC2626
Neutral:    #64748B
Palette categorical: 8–10 colors colorblind-friendly
```

Áp dụng trong `app/visualization/styles.py`.

---

## 10.6 Formatting

| Data | Format |
|------|--------|
| VND | `1.234.567 ₫` hoặc `1,234,567` + caption currency |
| Percent | `12.3%` |
| Compact large | `1.2M` optional on axis |
| Dates | `YYYY-MM-DD` or `MMM YYYY` |

---

## 10.7 Hàm factory (thiết kế API, chưa code)

```text
create_line_chart(df, x, y, color=None, title=...) -> go.Figure
create_bar_chart(df, x, y, orientation='v'|'h', title=...)
create_pie_chart(df, names, values, title=...)
create_area_chart(...)
create_scatter_chart(...)
create_histogram(...)
create_heatmap(df_matrix | long_df, ...)
create_treemap(df, path=[...], values=..., title=...)

# Matplotlib equivalents returning Figure or Axes for PDF
mpl_line(...), mpl_barh(...), save_fig(path, dpi=140)
```

**Input contract:** tidy DataFrame; không query bên trong visualization layer.

---

## 10.8 Performance

- Max points line: aggregate lên day/week nếu > 5000 raw points  
- Top-N trước khi bar  
- Treemap: top categories + "Other" bucket  

---

## 10.9 Checklist

- [ ] Plotly covers 8 chart types  
- [ ] Matplotlib for PDF core charts  
- [ ] styles palette shared  
- [ ] No DB access in visualization package  
- [ ] Formatters money/percent  
