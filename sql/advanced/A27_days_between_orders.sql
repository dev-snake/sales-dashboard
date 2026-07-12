-- ID: A27
-- Title: Days Between Orders
-- Skills: LAG diff
-- Tables: orders, customers
-- Params: none
-- Level: advanced

WITH ordered AS (
    SELECT
        c.code AS customer_code,
        o.order_date,
        LAG(o.order_date) OVER (
            PARTITION BY c.id
            ORDER BY o.order_date
        ) AS prev_order_date
    FROM customers c
    INNER JOIN orders o ON o.customer_id = c.id
    WHERE o.status IN ('paid', 'completed')
)
SELECT
    customer_code,
    order_date,
    prev_order_date,
    EXTRACT(EPOCH FROM (order_date - prev_order_date)) / 86400 AS days_since_prev
FROM ordered
WHERE prev_order_date IS NOT NULL
ORDER BY customer_code, order_date
LIMIT 200;
