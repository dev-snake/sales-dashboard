-- ID: B04
-- Title: High Value Orders
-- Skills: WHERE comparison
-- Tables: orders
-- Params: see comments in query
-- Level: basic

-- Param: min_total (example 1_000_000)
SELECT id, order_number, total_amount, status, order_date
FROM orders
WHERE total_amount > 1000000
ORDER BY total_amount DESC;
