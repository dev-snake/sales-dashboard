# SQL Catalog — Sales Analytics Dashboard

**135** ready-to-run PostgreSQL exercises on the project schema.  
Metric conventions: [`metrics.md`](./metrics.md).  
Optimization lab notes: [`optimization/notes.md`](./optimization/notes.md).

## Quick start

```bash
# List all
sales-dashboard sql list

# Filter by level
sales-dashboard sql list --level reporting

# Show SQL text
sales-dashboard sql show R04

# Execute against DB (requires migrate + seed)
sales-dashboard sql run R01
sales-dashboard sql run I14 --limit 20
```

Or with `psql`:

```bash
psql "$DATABASE_URL" -f sql/reporting/R04_top_products_by_revenue.sql
```

## Levels

| Folder | Count | Focus |
|--------|------:|-------|
| [`basic/`](./basic/) | 25 | SELECT, WHERE, ORDER BY, LIKE, BETWEEN, IN |
| [`intermediate/`](./intermediate/) | 30 | JOIN, GROUP BY, HAVING, CASE, subquery |
| [`advanced/`](./advanced/) | 35 | CTE, recursive CTE, window functions |
| [`reporting/`](./reporting/) | 30 | KPI, rankings, RFM, ABC, cohort, trends |
| [`optimization/`](./optimization/) | 15 | EXPLAIN, indexes, SARGability |
| **Total** | **135** | |

## File naming

```text
{ID}_{snake_title}.sql
```

Header format:

```sql
-- ID: R04
-- Title: Top Products By Revenue
-- Skills: Top N
-- Tables: orders, order_items, products
-- Params: :start_date, :end_date optional
-- Level: reporting
```

## Catalog index

### Basic (B01–B25)

| ID | File | Skills |
|----|------|--------|
| B01 | `B01_list_active_products.sql` | SELECT |
| B02 | `B02_customers_in_city.sql` | WHERE |
| B03 | `B03_orders_on_a_date.sql` | WHERE date |
| B04 | `B04_high_value_orders.sql` | comparison |
| B05 | `B05_sort_products_by_price.sql` | ORDER BY |
| B06 | `B06_top10_expensive_products.sql` | LIMIT |
| B07 | `B07_distinct_payment_methods.sql` | DISTINCT |
| B08 | `B08_distinct_customer_cities.sql` | DISTINCT |
| B09 | `B09_search_product_by_name.sql` | ILIKE |
| B10 | `B10_search_email_domain.sql` | LIKE |
| B11 | `B11_orders_in_date_range.sql` | BETWEEN |
| B12 | `B12_products_price_band.sql` | BETWEEN |
| B13 | `B13_orders_selected_stores.sql` | IN |
| B14 | `B14_orders_by_status_set.sql` | IN |
| B15 | `B15_null_email_customers.sql` | IS NULL |
| B16 | `B16_nonnull_phone_customers.sql` | IS NOT NULL |
| B17 | `B17_column_aliases.sql` | AS |
| B18 | `B18_computed_line_preview.sql` | arithmetic |
| B19 | `B19_employee_full_name.sql` | concat |
| B20 | `B20_date_parts_extract.sql` | EXTRACT |
| B21 | `B21_active_stores.sql` | boolean |
| B22 | `B22_exclude_cancelled_orders.sql` | NOT |
| B23 | `B23_pagination_pattern.sql` | LIMIT OFFSET |
| B24 | `B24_order_by_multiple.sql` | multi ORDER BY |
| B25 | `B25_case_insensitive_code.sql` | UPPER |

### Intermediate (I01–I30)

| ID | File | Skills |
|----|------|--------|
| I01 | `I01_orders_with_customers.sql` | INNER JOIN |
| I02 | `I02_order_lines_with_product.sql` | INNER JOIN |
| I03 | `I03_orders_store_region.sql` | multi JOIN |
| I04 | `I04_products_category_brand.sql` | multi JOIN |
| I05 | `I05_employees_with_store.sql` | INNER JOIN |
| I06 | `I06_orders_without_payments.sql` | anti-join |
| I07 | `I07_products_never_sold.sql` | anti-join |
| I08 | `I08_customers_no_orders.sql` | anti-join |
| I09 | `I09_stores_without_employees.sql` | anti-join |
| I10 | `I10_products_and_stock.sql` | LEFT JOIN |
| I11 | `I11_right_join_demo.sql` | RIGHT JOIN |
| I12 | `I12_full_join_demo.sql` | FULL JOIN |
| I13 | `I13_revenue_by_order.sql` | GROUP BY |
| I14 | `I14_revenue_by_store.sql` | GROUP BY |
| I15 | `I15_revenue_by_category.sql` | GROUP BY |
| I16 | `I16_orders_count_by_status.sql` | GROUP BY |
| I17 | `I17_aov_by_store.sql` | AVG |
| I18 | `I18_stores_revenue_above_threshold.sql` | HAVING |
| I19 | `I19_categories_with_many_products.sql` | HAVING |
| I20 | `I20_customers_at_least_3_orders.sql` | HAVING |
| I21 | `I21_payment_method_mix.sql` | GROUP BY |
| I22 | `I22_case_status_label.sql` | CASE |
| I23 | `I23_case_price_tier.sql` | CASE |
| I24 | `I24_case_region_performance.sql` | CASE + agg |
| I25 | `I25_products_above_avg_price.sql` | subquery |
| I26 | `I26_orders_above_avg_total.sql` | subquery |
| I27 | `I27_in_subquery_top_categories.sql` | IN subquery |
| I28 | `I28_exists_active_promo_orders.sql` | EXISTS |
| I29 | `I29_customer_last_order_date.sql` | correlated |
| I30 | `I30_derived_table_monthly_revenue.sql` | derived table |

### Advanced (A01–A35)

| ID | File | Skills |
|----|------|--------|
| A01–A07 | monthly CTE, multi CTE, recursive category/employee/region | CTE |
| A08–A14 | ROW_NUMBER, RANK, DENSE_RANK, NTILE, partitions | ranking windows |
| A15–A25 | running sum, moving avg, LAG/LEAD, FIRST_VALUE, CUME_DIST | value windows |
| A26–A35 | repeat purchase, velocity, returns, dedupe | business windows |

### Reporting (R01–R30)

| ID | Topic |
|----|--------|
| R01–R02 | Revenue / Profit KPI |
| R03–R08 | Margin by category, Top products/customers/employees/stores |
| R09–R16 | Breakdowns category/brand/region/store/time/DOW |
| R17–R20 | AOV, CLV, repeat rate |
| R21–R24 | ABC, Pareto, RFM |
| R25–R30 | Cohort, MoM trend, new/returning, payments, returns, net revenue |

### Optimization (O01–O15)

See [`optimization/notes.md`](./optimization/notes.md).

## Learning path

1. B01–B25 on seeded data  
2. I01–I30 joins & aggregates  
3. A01–A35 windows & CTE  
4. R01–R30 business reports  
5. O01–O15 EXPLAIN labs  

Design source: `docs/sql-roadmap.md`.
