-- ID: R13
-- Title: Sales By Month
-- Skills: time series
-- Tables: orders, order_items
-- Params: :start_date, :end_date optional (see comments)
-- Level: reporting

SELECT
    DATE_TRUNC('month', o.order_date) AS month_key,
    SUM(oi.line_total) AS revenue,
    COUNT(DISTINCT o.id) AS order_count
FROM order_items oi
INNER JOIN orders o ON o.id = oi.order_id
WHERE o.status IN ('paid', 'completed')
GROUP BY DATE_TRUNC('month', o.order_date)
ORDER BY month_key;
