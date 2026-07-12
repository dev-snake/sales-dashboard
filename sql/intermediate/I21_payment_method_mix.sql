-- ID: I21
-- Title: Payment Method Mix
-- Skills: GROUP BY
-- Tables: payments
-- Params: none
-- Level: intermediate

SELECT
    method,
    COUNT(*) AS payment_count,
    SUM(amount) AS total_amount
FROM payments
WHERE status = 'completed'
GROUP BY method
ORDER BY total_amount DESC;
