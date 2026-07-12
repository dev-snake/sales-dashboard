-- ID: R08
-- Title: Top Stores By Revenue
-- Skills: Top N
-- Tables: orders, order_items, stores
-- Params: :start_date, :end_date optional (see comments)
-- Level: reporting

SELECT
    s.code AS store_code,
    s.name AS store_name,
    COUNT(DISTINCT o.id) AS order_count,
    SUM(oi.line_total) AS revenue
FROM order_items oi
INNER JOIN orders o ON o.id = oi.order_id
INNER JOIN stores s ON s.id = o.store_id
WHERE o.status IN ('paid', 'completed')
GROUP BY s.code, s.name
ORDER BY revenue DESC
LIMIT 20;
