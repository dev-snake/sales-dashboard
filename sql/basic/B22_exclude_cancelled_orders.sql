-- ID: B22
-- Title: Exclude Cancelled Orders
-- Skills: WHERE NOT
-- Tables: orders
-- Params: see comments in query
-- Level: basic

SELECT id, order_number, status, total_amount, order_date
FROM orders
WHERE status <> 'cancelled'
ORDER BY order_date DESC
LIMIT 100;
