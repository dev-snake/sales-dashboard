-- ID: B11
-- Title: Orders In Date Range
-- Skills: BETWEEN
-- Tables: orders
-- Params: see comments in query
-- Level: basic

-- Params: start_date, end_date
SELECT id, order_number, order_date, total_amount, status
FROM orders
WHERE order_date >= DATE '2024-01-01'
  AND order_date <  DATE '2024-02-01'
ORDER BY order_date;
