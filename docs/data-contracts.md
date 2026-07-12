# Data contracts (ETL inbound)

Natural-key oriented files for Phase 5 ETL. Codes are resolved to FK ids at transform time.

## customers (CSV)

| Column | Type | Required | Notes |
|--------|------|----------|-------|
| code | string | yes | unique natural key |
| first_name | string | yes | |
| last_name | string | yes | |
| email | string | no | lowercased |
| phone | string | no | digits / +prefix |
| city | string | no | |
| region_code | string | no | → regions.code |
| registered_at | datetime | no | ISO / multi-format |
| gender | string | no | male/female/other/unknown |
| address | string | no | |
| is_active | bool | no | default true |

## products (Excel/CSV)

| Column | Type | Required | Notes |
|--------|------|----------|-------|
| sku | string | yes | unique |
| name | string | yes | |
| category_code | string | yes | → categories.code |
| brand_code | string | no | → brands.code |
| supplier_code | string | no | → suppliers.code |
| unit_price | decimal | yes | ≥ 0 |
| cost_price | decimal | yes | ≥ 0 |
| description | string | no | |
| is_active | bool | no | default true |

## orders (CSV)

| Column | Type | Required | Notes |
|--------|------|----------|-------|
| order_number | string | yes | unique |
| customer_code | string | yes | |
| store_code | string | yes | |
| employee_code | string | yes | |
| order_date | datetime | yes | |
| status | string | yes | pending/paid/completed/cancelled |
| subtotal | decimal | no | default 0 |
| discount_amount | decimal | no | |
| tax_amount | decimal | no | |
| total_amount | decimal | no | |
| notes | string | no | |

## order_items (CSV)

| Column | Type | Required | Notes |
|--------|------|----------|-------|
| order_number | string | yes | parent order |
| product_sku | string | yes | |
| quantity | int | yes | > 0 |
| unit_price | decimal | yes | snapshot |
| unit_cost | decimal | yes | snapshot |
| discount_amount | decimal | no | |
| line_total | decimal | no | computed if missing |

## payments (JSON array)

| Column | Type | Required | Notes |
|--------|------|----------|-------|
| payment_number | string | yes | unique |
| order_number | string | yes | |
| method | string | yes | cash/card/transfer/e_wallet/other |
| amount | decimal | yes | > 0 |
| status | string | yes | pending/completed/failed/refunded |
| paid_at | datetime | no | |

## Sample masters (`--ensure-masters` / `ensure_sample_masters`)

| Code | Entity |
|------|--------|
| REG-R01 | region |
| ST-HN-001 | store |
| EMP-MGR-0001 | employee |
| CAT-R01 | category |
| BR-0001 | brand |
| SUP-0001 | supplier |
