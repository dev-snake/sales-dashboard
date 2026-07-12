-- ID: A02
-- Title: Multi Cte Profit Report
-- Skills: multiple CTE
-- Tables: orders, order_items
-- Params: none
-- Level: advanced

WITH line_metrics AS (
    SELECT
        oi.order_id,
        oi.line_total AS revenue,
        oi.quantity * oi.unit_cost AS cogs
    FROM order_items oi
    INNER JOIN orders o ON o.id = oi.order_id
    WHERE o.status IN ('paid', 'completed')
),
totals AS (
    SELECT
        SUM(revenue) AS revenue,
        SUM(cogs) AS cogs
    FROM line_metrics
)
SELECT
    revenue,
    cogs,
    revenue - cogs AS gross_profit,
    ROUND(100.0 * (revenue - cogs) / NULLIF(revenue, 0), 2) AS gross_margin_pct
FROM totals;
