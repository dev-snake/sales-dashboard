-- ID: A34
-- Title: Payment Completion Lag
-- Skills: interval
-- Tables: payments, orders
-- Params: none
-- Level: advanced

SELECT
    o.order_number,
    o.order_date,
    p.paid_at,
    EXTRACT(EPOCH FROM (p.paid_at - o.order_date)) / 3600 AS hours_to_payment
FROM payments p
INNER JOIN orders o ON o.id = p.order_id
WHERE p.status = 'completed'
  AND p.paid_at IS NOT NULL
ORDER BY hours_to_payment DESC
LIMIT 100;
