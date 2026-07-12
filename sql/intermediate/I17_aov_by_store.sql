-- ID: I17
-- Title: Aov By Store
-- Skills: GROUP BY AVG
-- Tables: orders, stores
-- Params: none
-- Level: intermediate

SELECT
    s.code AS store_code,
    s.name AS store_name,
    COUNT(o.id) AS order_count,
    AVG(o.total_amount) AS avg_order_value
FROM orders o
INNER JOIN stores s ON s.id = o.store_id
WHERE o.status IN ('paid', 'completed')
GROUP BY s.code, s.name
ORDER BY avg_order_value DESC;
