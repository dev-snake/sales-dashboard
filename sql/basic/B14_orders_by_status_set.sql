-- ID: B14
-- Title: Orders By Status Set
-- Skills: IN
-- Tables: orders
-- Params: see comments in query
-- Level: basic

SELECT id, order_number, status, total_amount, order_date
FROM orders
WHERE status IN ('paid', 'completed')
ORDER BY order_date DESC;
