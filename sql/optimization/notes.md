# SQL Optimization lab notes

Use these exercises after seed data is loaded (`seed run --scale 10k` recommended for meaningful plans).

## How to run

```bash
# Via CLI
sales-dashboard sql run --id O01
sales-dashboard sql run --id O02

# Or psql
psql "$DATABASE_URL" -f sql/optimization/O01_explain_revenue_by_store.sql
```

## Checklist per exercise

| ID | Goal | What to look for |
|----|------|------------------|
| O01 | Read EXPLAIN | Seq Scan vs Index Scan, Hash Join / Nested Loop |
| O02 | EXPLAIN ANALYZE | actual time, rows, buffers |
| O03 | Selective equality | Index on `order_number` (unique) → Index Scan |
| O04 | Date range | `ix_orders_order_date` or bitmap index scan |
| O05 | Composite store+date | `ix_orders_store_date` |
| O06 | Composite status+date | `ix_orders_status_date` |
| O07 | product_id aggregate | `ix_order_items_product_id` |
| O08 | Covering index | Index Only Scan after INCLUDE |
| O09 | SELECT * | narrower projection reduces I/O |
| O10 | SARGability | range on raw `order_date` |
| O11 | Filter fact early | less rows into join |
| O12 | CTE materialize | MATERIALIZED vs NOT MATERIALIZED |
| O13 | Partial index | `ix_inventory_low_stock` |
| O14 | ANALYZE/VACUUM | stats freshness in `pg_stat_user_tables` |
| O15 | HAVING vs subquery | often similar plans — verify |

## Before / after template

Record on your machine after seed:

| Query | Scale | Planning (ms) | Execution (ms) | Notes |
|-------|-------|---------------|----------------|-------|
| I14 / O02 | 10k | | | baseline |
| O05 | 10k | | | composite |

## Existing indexes (from schema)

See `docs/database-design.md` — key ones for labs:

- `ix_orders_order_date`
- `ix_orders_store_date (store_id, order_date)`
- `ix_orders_status_date (status, order_date)`
- `ix_order_items_product_id`
- `ix_inventory_low_stock` (partial)

## Tips

1. Run `ANALYZE` after large seed.  
2. Disable `seqscan` only for experiments: `SET enable_seqscan = off;` (reset after).  
3. Prefer fixing queries / indexes over forcing planner settings in app code.
