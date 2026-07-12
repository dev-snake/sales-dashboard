-- ID: I01
-- Title: Orders With Customers
-- Skills: INNER JOIN
-- Tables: orders, customers
-- Params: none
-- Level: intermediate

SELECT
    o.id AS order_id,
    o.order_number,
    o.order_date,
    o.total_amount,
    c.code AS customer_code,
    c.first_name || ' ' || c.last_name AS customer_name
FROM orders o
INNER JOIN customers c ON c.id = o.customer_id
ORDER BY o.order_date DESC
LIMIT 100;
