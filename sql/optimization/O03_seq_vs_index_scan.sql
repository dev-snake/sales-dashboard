-- ID: O03
-- Title: Seq Vs Index Scan
-- Skills: selectivity
-- Tables: orders
-- Params: none
-- Level: optimization

-- Lab: selective filter tends to prefer Index Scan
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, order_number, order_date, total_amount
FROM orders
WHERE order_number = 'ORD-000000001';
