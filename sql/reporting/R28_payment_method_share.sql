-- ID: R28
-- Title: Payment Method Share
-- Skills: share
-- Tables: payments
-- Params: :start_date, :end_date optional (see comments)
-- Level: reporting

SELECT
    method,
    COUNT(*) AS payment_count,
    SUM(amount) AS total_amount,
    ROUND(100.0 * SUM(amount) / SUM(SUM(amount)) OVER (), 2) AS pct_of_amount
FROM payments
WHERE status = 'completed'
GROUP BY method
ORDER BY total_amount DESC;
