-- ID: R11
-- Title: Sales By Region
-- Skills: breakdown
-- Tables: orders, order_items, stores, regions
-- Params: :start_date, :end_date optional (see comments)
-- Level: reporting

SELECT
    r.name AS region_name,
    SUM(oi.line_total) AS revenue,
    COUNT(DISTINCT o.id) AS order_count
FROM order_items oi
INNER JOIN orders o ON o.id = oi.order_id
INNER JOIN stores s ON s.id = o.store_id
INNER JOIN regions r ON r.id = s.region_id
WHERE o.status IN ('paid', 'completed')
GROUP BY r.name
ORDER BY revenue DESC;
