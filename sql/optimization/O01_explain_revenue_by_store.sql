-- ID: O01
-- Title: Explain Revenue By Store
-- Skills: EXPLAIN
-- Tables: orders, order_items, stores
-- Params: none
-- Level: optimization

-- Lab: read EXPLAIN plan for I14-style revenue by store
EXPLAIN
SELECT
    s.code AS store_code,
    SUM(oi.line_total) AS revenue
FROM orders o
INNER JOIN order_items oi ON oi.order_id = o.id
INNER JOIN stores s ON s.id = o.store_id
WHERE o.status IN ('paid', 'completed')
GROUP BY s.code
ORDER BY revenue DESC;
