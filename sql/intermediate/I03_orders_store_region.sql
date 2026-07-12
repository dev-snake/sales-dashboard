-- ID: I03
-- Title: Orders Store Region
-- Skills: multi JOIN
-- Tables: orders, stores, regions
-- Params: none
-- Level: intermediate

SELECT
    o.order_number,
    o.order_date,
    o.total_amount,
    s.code AS store_code,
    s.name AS store_name,
    r.code AS region_code,
    r.name AS region_name
FROM orders o
INNER JOIN stores s ON s.id = o.store_id
INNER JOIN regions r ON r.id = s.region_id
ORDER BY o.order_date DESC
LIMIT 100;
