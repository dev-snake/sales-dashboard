-- ID: A15
-- Title: Running Total Revenue
-- Skills: SUM OVER
-- Tables: orders, order_items
-- Params: none
-- Level: advanced

WITH daily AS (
    SELECT
        o.order_date::date AS day,
        SUM(oi.line_total) AS revenue
    FROM order_items oi
    INNER JOIN orders o ON o.id = oi.order_id
    WHERE o.status IN ('paid', 'completed')
    GROUP BY o.order_date::date
)
SELECT
    day,
    revenue,
    SUM(revenue) OVER (ORDER BY day ROWS UNBOUNDED PRECEDING) AS running_revenue
FROM daily
ORDER BY day;
