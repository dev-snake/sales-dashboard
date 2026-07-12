-- ID: B24
-- Title: Order By Multiple
-- Skills: ORDER BY multi
-- Tables: orders
-- Params: see comments in query
-- Level: basic

SELECT id, order_number, status, order_date, total_amount
FROM orders
ORDER BY status ASC, order_date DESC
LIMIT 100;
