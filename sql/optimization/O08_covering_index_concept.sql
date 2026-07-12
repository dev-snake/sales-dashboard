-- ID: O08
-- Title: Covering Index Concept
-- Skills: INCLUDE index
-- Tables: orders
-- Params: none
-- Level: optimization

-- Lab note: covering index example (run as DBA exercise; may already exist partial)
-- CREATE INDEX CONCURRENTLY ix_orders_status_date_covering
--   ON orders (status, order_date) INCLUDE (total_amount, order_number);
-- Then re-run EXPLAIN for O06 and look for Index Only Scan.
EXPLAIN
SELECT order_number, total_amount, order_date
FROM orders
WHERE status = 'completed'
  AND order_date >= CURRENT_DATE - INTERVAL '30 days';
