-- ID: O02
-- Title: Explain Analyze Revenue By Store
-- Skills: EXPLAIN ANALYZE
-- Tables: orders, order_items, stores
-- Params: none
-- Level: optimization

-- Lab: EXPLAIN ANALYZE (runs the query) — compare before/after indexes
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT
    s.code AS store_code,
    SUM(oi.line_total) AS revenue
FROM orders o
INNER JOIN order_items oi ON oi.order_id = o.id
INNER JOIN stores s ON s.id = o.store_id
WHERE o.status IN ('paid', 'completed')
GROUP BY s.code
ORDER BY revenue DESC;
