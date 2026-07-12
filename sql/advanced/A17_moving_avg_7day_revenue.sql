-- ID: A17
-- Title: Moving Avg 7Day Revenue
-- Skills: AVG frame
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
    AVG(revenue) OVER (
        ORDER BY day
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS moving_avg_7d
FROM daily
ORDER BY day;
