-- ID: R04
-- Title: Top Products By Revenue
-- Skills: Top N
-- Tables: orders, order_items, products
-- Params: :start_date, :end_date optional (see comments)
-- Level: reporting

SELECT
    p.sku,
    p.name,
    SUM(oi.quantity) AS units_sold,
    SUM(oi.line_total) AS revenue
FROM order_items oi
INNER JOIN orders o ON o.id = oi.order_id
INNER JOIN products p ON p.id = oi.product_id
WHERE o.status IN ('paid', 'completed')
GROUP BY p.sku, p.name
ORDER BY revenue DESC
LIMIT 20;
