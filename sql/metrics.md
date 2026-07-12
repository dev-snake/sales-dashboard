# Metric definitions (single source of truth for SQL)

Apply consistently in reporting / advanced analytics queries.

| Metric | SQL definition |
|--------|----------------|
| **Revenue** | `SUM(order_items.line_total)` for orders with `status IN ('paid','completed')` |
| **COGS** | `SUM(order_items.quantity * order_items.unit_cost)` same filter |
| **Gross Profit** | Revenue − COGS |
| **Gross Margin %** | `100 * Gross Profit / NULLIF(Revenue, 0)` |
| **Orders count** | `COUNT(DISTINCT orders.id)` with status filter above |
| **AOV** | Revenue / Orders count |
| **Units sold** | `SUM(order_items.quantity)` |
| **Net revenue** | Revenue − `SUM(returns.refund_amount)` where return status in `approved`,`completed` |

## Soft-delete

Master tables: prefer `deleted_at IS NULL` when selecting active entities.

## Date filters

Prefer SARGable ranges:

```sql
order_date >= :start_date
AND order_date <  :end_date   -- exclusive end
```

Avoid `DATE(order_date) = ...` on large tables (see O10).
