-- ID: I14
-- Title: Revenue By Store
-- Skills: GROUP BY
-- Tables: orders, order_items, stores
-- Params: none
-- Level: intermediate

SELECT
    s.id AS store_id,
    s.code AS store_code,
    s.name AS store_name,
    SUM(oi.line_total) AS revenue
FROM orders o
INNER JOIN order_items oi ON oi.order_id = o.id
INNER JOIN stores s ON s.id = o.store_id
WHERE o.status IN ('paid', 'completed')
GROUP BY s.id, s.code, s.name
ORDER BY revenue DESC;
