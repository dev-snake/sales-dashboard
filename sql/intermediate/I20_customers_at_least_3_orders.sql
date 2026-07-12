-- ID: I20
-- Title: Customers At Least 3 Orders
-- Skills: HAVING
-- Tables: customers, orders
-- Params: none
-- Level: intermediate

SELECT
    c.code AS customer_code,
    c.first_name || ' ' || c.last_name AS customer_name,
    COUNT(o.id) AS order_count
FROM customers c
INNER JOIN orders o ON o.customer_id = c.id
WHERE o.status IN ('paid', 'completed')
GROUP BY c.code, c.first_name, c.last_name
HAVING COUNT(o.id) >= 3
ORDER BY order_count DESC;
