-- ID: A26
-- Title: Repeat Purchase Flag
-- Skills: LAG per customer
-- Tables: orders, customers
-- Params: none
-- Level: advanced

WITH ordered AS (
    SELECT
        c.id AS customer_id,
        c.code AS customer_code,
        o.id AS order_id,
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
    order_id,
    order_date,
    prev_order_date,
    prev_order_date IS NOT NULL AS is_repeat_purchase
FROM ordered
ORDER BY customer_code, order_date
LIMIT 200;
