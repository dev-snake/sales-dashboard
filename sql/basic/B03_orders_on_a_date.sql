-- ID: B03
-- Title: Orders On A Date
-- Skills: WHERE date
-- Tables: orders
-- Params: see comments in query
-- Level: basic

-- Param: target date (example: current_date - 7)
SELECT id, order_number, order_date, status, total_amount
FROM orders
WHERE order_date::date = CURRENT_DATE - INTERVAL '7 days';
