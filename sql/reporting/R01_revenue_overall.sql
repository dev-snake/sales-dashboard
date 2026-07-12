-- ID: R01
-- Title: Revenue Overall
-- Skills: aggregate
-- Tables: orders, order_items
-- Params: :start_date, :end_date optional (see comments)
-- Level: reporting

-- Params: :start_date, :end_date (optional filters — examples below)
SELECT
    SUM(oi.line_total) AS revenue
FROM order_items oi
INNER JOIN orders o ON o.id = oi.order_id
WHERE o.status IN ('paid', 'completed')
  AND o.order_date >= CURRENT_DATE - INTERVAL '30 days';
