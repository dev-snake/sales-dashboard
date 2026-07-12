-- ID: O05
-- Title: Composite Store Date
-- Skills: composite index
-- Tables: orders
-- Params: none
-- Level: optimization

-- Lab: dashboard pattern uses (store_id, order_date)
-- Index: ix_orders_store_date
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, order_number, total_amount, order_date
FROM orders
WHERE store_id = 1
  AND order_date >= CURRENT_DATE - INTERVAL '90 days'
ORDER BY order_date DESC;
