-- ID: O06
-- Title: Composite Status Date
-- Skills: composite index
-- Tables: orders
-- Params: none
-- Level: optimization

-- Index: ix_orders_status_date
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, order_number, total_amount
FROM orders
WHERE status = 'completed'
  AND order_date >= CURRENT_DATE - INTERVAL '90 days';
