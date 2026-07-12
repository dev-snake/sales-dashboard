-- ID: A29
-- Title: Best Selling Day Of Week
-- Skills: window + calendar
-- Tables: orders, order_items, calendar
-- Params: none
-- Level: advanced

WITH daily AS (
    SELECT
        cal.day_name,
        cal.day_of_week,
        SUM(oi.line_total) AS revenue
    FROM order_items oi
    INNER JOIN orders o ON o.id = oi.order_id
    INNER JOIN calendar cal ON cal.full_date = o.order_date::date
    WHERE o.status IN ('paid', 'completed')
    GROUP BY cal.day_name, cal.day_of_week
)
SELECT
    day_name,
    day_of_week,
    revenue,
    RANK() OVER (ORDER BY revenue DESC) AS dow_rank
FROM daily
ORDER BY day_of_week;
