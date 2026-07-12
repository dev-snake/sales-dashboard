-- ID: O09
-- Title: Avoid Select Star
-- Skills: rewrite
-- Tables: orders, customers
-- Params: none
-- Level: optimization

-- Bad: SELECT * pulls unused wide rows
-- SELECT * FROM orders o JOIN customers c ON c.id = o.customer_id LIMIT 100;
-- Good: project only needed columns
SELECT
    o.order_number,
    o.order_date,
    o.total_amount,
    c.code AS customer_code
FROM orders o
INNER JOIN customers c ON c.id = o.customer_id
ORDER BY o.order_date DESC
LIMIT 100;
