-- ID: A22
-- Title: Last Order Date Per Customer
-- Skills: LAST_VALUE / MAX
-- Tables: orders, customers
-- Params: none
-- Level: advanced

SELECT
    c.code AS customer_code,
    MAX(o.order_date) AS last_order_date
FROM customers c
INNER JOIN orders o ON o.customer_id = c.id
WHERE o.status IN ('paid', 'completed')
GROUP BY c.code
ORDER BY last_order_date DESC
LIMIT 200;
