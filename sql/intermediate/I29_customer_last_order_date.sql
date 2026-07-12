-- ID: I29
-- Title: Customer Last Order Date
-- Skills: correlated subquery
-- Tables: customers, orders
-- Params: none
-- Level: intermediate

SELECT
    c.code,
    c.first_name || ' ' || c.last_name AS customer_name,
    (
        SELECT MAX(o.order_date)
        FROM orders o
        WHERE o.customer_id = c.id
          AND o.status IN ('paid', 'completed')
    ) AS last_order_date
FROM customers c
WHERE c.deleted_at IS NULL
ORDER BY last_order_date DESC NULLS LAST
LIMIT 100;
