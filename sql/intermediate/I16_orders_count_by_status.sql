-- ID: I16
-- Title: Orders Count By Status
-- Skills: GROUP BY
-- Tables: orders
-- Params: none
-- Level: intermediate

SELECT
    status,
    COUNT(*) AS order_count
FROM orders
GROUP BY status
ORDER BY order_count DESC;
