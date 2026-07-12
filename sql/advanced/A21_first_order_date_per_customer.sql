-- ID: A21
-- Title: First Order Date Per Customer
-- Skills: FIRST_VALUE
-- Tables: orders, customers
-- Params: none
-- Level: advanced

SELECT DISTINCT
    c.code AS customer_code,
    FIRST_VALUE(o.order_date) OVER (
        PARTITION BY c.id
        ORDER BY o.order_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) AS first_order_date
FROM customers c
INNER JOIN orders o ON o.customer_id = c.id
WHERE o.status IN ('paid', 'completed')
ORDER BY customer_code
LIMIT 200;
