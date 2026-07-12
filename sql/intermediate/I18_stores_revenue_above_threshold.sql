-- ID: I18
-- Title: Stores Revenue Above Threshold
-- Skills: HAVING
-- Tables: orders, order_items, stores
-- Params: none
-- Level: intermediate

-- Param: min_revenue (example 5_000_000)
SELECT
    s.code AS store_code,
    SUM(oi.line_total) AS revenue
FROM orders o
INNER JOIN order_items oi ON oi.order_id = o.id
INNER JOIN stores s ON s.id = o.store_id
WHERE o.status IN ('paid', 'completed')
GROUP BY s.code
HAVING SUM(oi.line_total) > 5000000
ORDER BY revenue DESC;
