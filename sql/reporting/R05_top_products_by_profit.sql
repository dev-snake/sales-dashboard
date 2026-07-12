-- ID: R05
-- Title: Top Products By Profit
-- Skills: Top N
-- Tables: orders, order_items, products
-- Params: :start_date, :end_date optional (see comments)
-- Level: reporting

SELECT
    p.sku,
    p.name,
    SUM(oi.line_total) AS revenue,
    SUM(oi.quantity * oi.unit_cost) AS cogs,
    SUM(oi.line_total) - SUM(oi.quantity * oi.unit_cost) AS gross_profit
FROM order_items oi
INNER JOIN orders o ON o.id = oi.order_id
INNER JOIN products p ON p.id = oi.product_id
WHERE o.status IN ('paid', 'completed')
GROUP BY p.sku, p.name
ORDER BY gross_profit DESC
LIMIT 20;
