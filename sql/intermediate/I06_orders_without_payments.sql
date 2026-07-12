-- ID: I06
-- Title: Orders Without Payments
-- Skills: LEFT JOIN anti-join
-- Tables: orders, payments
-- Params: none
-- Level: intermediate

SELECT
    o.id,
    o.order_number,
    o.status,
    o.total_amount,
    o.order_date
FROM orders o
LEFT JOIN payments p ON p.order_id = o.id
WHERE p.id IS NULL
ORDER BY o.order_date DESC;
