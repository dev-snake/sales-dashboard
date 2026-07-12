-- ID: I30
-- Title: Derived Table Monthly Revenue
-- Skills: derived table
-- Tables: orders, order_items
-- Params: none
-- Level: intermediate

SELECT
    month_key,
    revenue
FROM (
    SELECT
        DATE_TRUNC('month', o.order_date) AS month_key,
        SUM(oi.line_total) AS revenue
    FROM order_items oi
    INNER JOIN orders o ON o.id = oi.order_id
    WHERE o.status IN ('paid', 'completed')
    GROUP BY DATE_TRUNC('month', o.order_date)
) monthly
ORDER BY month_key;
