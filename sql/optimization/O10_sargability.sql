-- ID: O10
-- Title: Sargability
-- Skills: SARGable predicates
-- Tables: orders
-- Params: none
-- Level: optimization

-- Non-SARGable (wraps column — may prevent index use):
-- WHERE DATE(order_date) = CURRENT_DATE
-- SARGable rewrite:
SELECT id, order_number, order_date, total_amount
FROM orders
WHERE order_date >= CURRENT_DATE
  AND order_date <  CURRENT_DATE + INTERVAL '1 day';
