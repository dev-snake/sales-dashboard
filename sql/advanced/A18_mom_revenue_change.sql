-- ID: A18
-- Title: Mom Revenue Change
-- Skills: LAG
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
SELECT
    month_key,
    revenue,
    LAG(revenue) OVER (ORDER BY month_key) AS prev_month_revenue,
    revenue - LAG(revenue) OVER (ORDER BY month_key) AS mom_change,
    ROUND(
        100.0 * (revenue - LAG(revenue) OVER (ORDER BY month_key))
        / NULLIF(LAG(revenue) OVER (ORDER BY month_key), 0),
        2
    ) AS mom_pct
FROM monthly
ORDER BY month_key;
