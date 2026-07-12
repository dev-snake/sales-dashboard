-- ID: A01
-- Title: Monthly Revenue Cte
-- Skills: CTE
-- Tables: orders, order_items
-- Params: none
-- Level: advanced

WITH monthly AS (
    SELECT
        DATE_TRUNC('month', o.order_date) AS month_key,
        SUM(oi.line_total) AS revenue
    FROM order_items oi
    INNER JOIN orders o ON o.id = oi.order_id
    WHERE o.status IN ('paid', 'completed')
    GROUP BY DATE_TRUNC('month', o.order_date)
)
SELECT month_key, revenue
FROM monthly
ORDER BY month_key;
