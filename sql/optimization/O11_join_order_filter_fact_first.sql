-- ID: O11
-- Title: Join Order Filter Fact First
-- Skills: join filters
-- Tables: orders, order_items, products
-- Params: none
-- Level: optimization

-- Prefer filtering large fact early (orders by date/status) then join dimensions
SELECT
    p.sku,
    SUM(oi.line_total) AS revenue
FROM orders o
INNER JOIN order_items oi ON oi.order_id = o.id
INNER JOIN products p ON p.id = oi.product_id
WHERE o.status IN ('paid', 'completed')
  AND o.order_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY p.sku
ORDER BY revenue DESC
LIMIT 20;
