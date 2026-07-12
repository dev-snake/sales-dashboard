# 12. Seed Data Design

## 12.1 Mục tiêu

Sinh dữ liệu **giả nhưng chân thực** phản ánh chuỗi bán lẻ multi-store để:

- Luyện SQL ở nhiều scale  
- Demo dashboard mượt  
- Stress nhẹ index/query ở 100K–1M  
- Không cần dữ liệu công ty thật  

Công cụ: **Faker** (locale `vi_VN` + fallback), **numpy** random distributions, business rules.

CLI:

```text
seed run --scale 100|1k|10k|100k|1m [--locale vi_VN] [--reset]
```

---

## 12.2 Scale tiers

Scale hiểu theo **số orders** (fact chính). Bảng khác derive theo tỷ lệ.

| Tier | Flag | Orders | Order items (avg 2.5/line) | Customers | Products | Stores | Employees |
|------|------|--------|----------------------------|-----------|----------|--------|-----------|
| XS | `100` | 100 | ~250 | 80 | 50 | 3 | 10 |
| S | `1k` | 1_000 | ~2_500 | 600 | 150 | 5 | 25 |
| M | `10k` | 10_000 | ~25_000 | 4_000 | 400 | 10 | 60 |
| L | `100k` | 100_000 | ~250_000 | 30_000 | 1_000 | 20 | 150 |
| XL | `1m` | 1_000_000 | ~2_500_000 | 200_000 | 2_000 | 40 | 400 |

### Master & satellite counts (gợi ý)

| Entity | XS | S | M | L | XL |
|--------|----|----|----|----|-----|
| regions | 5 | 8 | 12 | 16 | 20 |
| categories | 8 | 12 | 20 | 30 | 40 |
| brands | 10 | 20 | 40 | 80 | 120 |
| suppliers | 5 | 10 | 20 | 40 | 60 |
| promotions | 5 | 15 | 30 | 50 | 80 |
| payments | ~1.05 × orders | (partial multi-pay ~5%) | | | |
| returns | 2–5% of items | | | | |
| inventory rows | stores × products (sparse 70% filled) | | | | |
| stock_movements | ~3–8 × order_items magnitude (simplified generator) | | | | |
| calendar | fixed 2020-01-01 → 2030-12-31 all tiers | | | | |

---

## 12.3 Time span

| Tier | order_date range |
|------|------------------|
| XS–S | last 6 months |
| M | last 18 months |
| L–XL | last 36 months |

Seasonality: tăng doanh số tháng 11–12, Tết (Jan/Feb dương lịch approx), weekend uplift +15–25%.

---

## 12.4 Phân phối thực tế (distributions)

### Customers

- 60% có email, 80% có phone  
- Power-law orders: top 20% customers tạo ~70% orders (Pareto-ish)  
- `registered_at` trước first order  

### Products

- Price log-normal trong band category  
- `cost_price` = unit_price × Uniform(0.55, 0.85)  
- 10% products inactive  
- SKU pattern: `CAT-BRAND-######`  

### Orders

- Status: completed 75%, paid 15%, pending 5%, cancelled 5%  
- Items per order: Poisson λ=2.5 clipped [1, 12]  
- Discount: 30% orders có line discount nhỏ; 10% có promotion_id  
- Tax: 0 hoặc 8–10% config (chốt **8%** trên subtotal after discount)  
- Employee thuộc cùng store với order  

### Payments

- completed payments cho paid/completed orders  
- Methods: cash 40%, card 35%, transfer 15%, e_wallet 10%  
- 5% orders multi-payment (2 rows)  

### Inventory

- quantity_on_hand: Heavy-tailed; 5% below reorder_level  
- reorder_level by category  

### Returns

- Reasons weighted: changed_mind 40%, defective 25%, wrong_item 20%, other 15%  
- Only from completed/paid orders  

### Regions / Stores

- Vietnam-inspired names (HN, HCM, DN, HP, CT…) without claiming real store brands  
- Employees: 1 manager / store + associates; manager_id tree depth 2  

---

## 12.5 Referential integrity rules khi sinh

1. Generate masters first (regions → stores → employees → … → products → customers → promotions → calendar).  
2. Orders only reference existing FKs.  
3. order_items prices snapshot from product at generation time (± small noise optional).  
4. stock_movements `sale_out` aligned with completed order items (best-effort).  
5. returns.quantity ≤ order_item.quantity.  
6. Unique natural keys guaranteed (sequences + Faker unique).  

---

## 12.6 Performance strategy by tier

| Tier | Strategy |
|------|----------|
| ≤10k | ORM bulk_save_objects / simple inserts OK |
| 100k | `session.execute(insert(), list_of_dicts)` batches 2k–5k |
| 1m | psycopg `COPY` or multi-row INSERT batches; disable indexes temporarily optional P2; progress logs |

**Memory:** generate in chunks (e.g., 10k orders/chunk) for L/XL.

**Determinism:** `--seed 42` cho numpy/random/Faker seed → reproducible tests.

---

## 12.7 Module design

```text
app/services/seed_service.py
app/etl or app/seed/
  generators/
    regions.py
    stores.py
    ...
    orders.py
  distributions.py
  scale_config.py
```

`scale_config.py` maps tier → counts dict.

---

## 12.8 Reset policy

```text
seed run --reset --scale 10k
```

1. TRUNCATE tables CASCADE theo thứ tự an toàn (hoặc drop/recreate via alembic)  
2. Reseed calendar  
3. Generate  

**Cảnh báo:** destructive — CLI confirm flag `--yes`.

---

## 12.9 Sample export for ETL demos

Ngoài DB seed, export **mẫu nhỏ** ra `data/raw/samples/`:

- 50 customers CSV  
- 30 products Excel  
- 20 orders + items CSV  
- payments JSON  

Phục vụ Phase ETL không phụ thuộc full seed.

---

## 12.10 Data realism checklist

- [x] Seasonality weights in date sampler (Nov/Dec/Tết + weekend)  
- [x] Pareto: power-law customer/product order assignment  
- [x] Status mix includes cancelled/pending  
- [x] Low stock ~5% inventory rows  
- [x] Manager hierarchy (1 manager/store + associates)  
- [x] Categories multi-level parent_id  
- [x] Sample export for ETL  
- [ ] Validate on live DB after first `seed run` (seasonality chart, RFM spread)  

---

## 12.11 Privacy

Faker data only — không dùng dataset khách hàng thật.  
README ghi rõ synthetic.
