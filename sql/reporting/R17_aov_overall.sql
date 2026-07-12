-- ID: R17
-- Title: Aov Overall
-- Skills: KPI
-- Tables: orders, order_items
-- Params: :start_date, :end_date optional (see comments)
-- Level: reporting

WITH metrics AS (
    SELECT
        SUM(oi.line_total) AS revenue,
        COUNT(DISTINCT o.id) AS order_count
    FROM order_items oi
    INNER JOIN orders o ON o.id = oi.order_id
    WHERE o.status IN ('paid', 'completed')
)
SELECT
    revenue,
    order_count,
    revenue / NULLIF(order_count, 0) AS aov
FROM metrics;
