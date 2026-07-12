-- ID: O04
-- Title: Index On Order Date
-- Skills: index usage
-- Tables: orders
-- Params: none
-- Level: optimization

-- Lab: range filter on order_date (index ix_orders_order_date)
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, order_number, total_amount
FROM orders
WHERE order_date >= CURRENT_DATE - INTERVAL '30 days'
  AND order_date <  CURRENT_DATE
  AND status IN ('paid', 'completed');
