-- ID: O15
-- Title: Having Vs Subquery Rewrite
-- Skills: equivalent plans
-- Tables: orders, order_items, stores
-- Params: none
-- Level: optimization

-- Form A: HAVING
SELECT s.code, SUM(oi.line_total) AS revenue
FROM stores s
INNER JOIN orders o ON o.store_id = s.id
INNER JOIN order_items oi ON oi.order_id = o.id
WHERE o.status IN ('paid', 'completed')
GROUP BY s.code
HAVING SUM(oi.line_total) > 1000000;

-- Form B: subquery filter (compare EXPLAIN ANALYZE of both)
-- SELECT * FROM (
--   SELECT s.code, SUM(oi.line_total) AS revenue
--   FROM stores s
--   INNER JOIN orders o ON o.store_id = s.id
--   INNER JOIN order_items oi ON oi.order_id = o.id
--   WHERE o.status IN ('paid', 'completed')
--   GROUP BY s.code
-- ) t
-- WHERE revenue > 1000000;
