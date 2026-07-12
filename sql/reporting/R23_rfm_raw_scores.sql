-- ID: R23
-- Title: Rfm Raw Scores
-- Skills: RFM
-- Tables: orders, order_items, customers
-- Params: :start_date, :end_date optional (see comments)
-- Level: reporting

WITH base AS (
    SELECT
        c.id AS customer_id,
        c.code AS customer_code,
        MAX(o.order_date)::date AS last_order_date,
        COUNT(DISTINCT o.id) AS frequency,
        SUM(oi.line_total) AS monetary
    FROM customers c
    INNER JOIN orders o ON o.customer_id = c.id
    INNER JOIN order_items oi ON oi.order_id = o.id
    WHERE o.status IN ('paid', 'completed')
    GROUP BY c.id, c.code
)
SELECT
    customer_code,
    last_order_date,
    (CURRENT_DATE - last_order_date) AS recency_days,
    frequency,
    monetary
FROM base
ORDER BY monetary DESC
LIMIT 200;
