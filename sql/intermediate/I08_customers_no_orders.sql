-- ID: I08
-- Title: Customers No Orders
-- Skills: LEFT JOIN anti-join
-- Tables: customers, orders
-- Params: none
-- Level: intermediate

SELECT
    c.id,
    c.code,
    c.first_name,
    c.last_name,
    c.email
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.id
WHERE o.id IS NULL
  AND c.deleted_at IS NULL
ORDER BY c.code;
