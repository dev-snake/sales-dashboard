-- ID: I24
-- Title: Case Region Performance
-- Skills: CASE WHEN + aggregate
-- Tables: orders, order_items, stores, regions
-- Params: none
-- Level: intermediate

SELECT
    r.name AS region_name,
    SUM(oi.line_total) AS revenue,
    CASE
        WHEN SUM(oi.line_total) >= 20000000 THEN 'High'
        WHEN SUM(oi.line_total) >= 5000000  THEN 'Medium'
        ELSE 'Low'
    END AS performance_band
FROM order_items oi
INNER JOIN orders o ON o.id = oi.order_id
INNER JOIN stores s ON s.id = o.store_id
INNER JOIN regions r ON r.id = s.region_id
WHERE o.status IN ('paid', 'completed')
GROUP BY r.name
ORDER BY revenue DESC;
