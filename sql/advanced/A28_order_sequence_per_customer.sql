-- ID: A28
-- Title: Order Sequence Per Customer
-- Skills: ROW_NUMBER per customer
-- Tables: orders, customers
-- Params: none
-- Level: advanced

SELECT
    c.code AS customer_code,
    o.order_number,
    o.order_date,
    o.total_amount,
    ROW_NUMBER() OVER (
        PARTITION BY c.id
        ORDER BY o.order_date
    ) AS order_seq
FROM customers c
INNER JOIN orders o ON o.customer_id = c.id
WHERE o.status IN ('paid', 'completed')
ORDER BY customer_code, order_seq
LIMIT 200;
