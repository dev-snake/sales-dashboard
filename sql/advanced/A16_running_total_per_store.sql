-- ID: A16
-- Title: Running Total Per Store
-- Skills: SUM PARTITION
-- Tables: orders, order_items, stores
-- Params: none
-- Level: advanced

WITH daily_store AS (
    SELECT
        s.code AS store_code,
        o.order_date::date AS day,
        SUM(oi.line_total) AS revenue
    FROM order_items oi
    INNER JOIN orders o ON o.id = oi.order_id
    INNER JOIN stores s ON s.id = o.store_id
    WHERE o.status IN ('paid', 'completed')
    GROUP BY s.code, o.order_date::date
)
SELECT
    store_code,
    day,
    revenue,
    SUM(revenue) OVER (
        PARTITION BY store_code
        ORDER BY day
        ROWS UNBOUNDED PRECEDING
    ) AS running_revenue
FROM daily_store
ORDER BY store_code, day;
