-- ID: R14
-- Title: Sales By Quarter
-- Skills: time series
-- Tables: orders, order_items
-- Params: :start_date, :end_date optional (see comments)
-- Level: reporting

SELECT
    EXTRACT(YEAR FROM o.order_date)::int AS year,
    EXTRACT(QUARTER FROM o.order_date)::int AS quarter,
    SUM(oi.line_total) AS revenue,
    COUNT(DISTINCT o.id) AS order_count
FROM order_items oi
INNER JOIN orders o ON o.id = oi.order_id
WHERE o.status IN ('paid', 'completed')
GROUP BY 1, 2
ORDER BY 1, 2;
