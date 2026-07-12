-- ID: I22
-- Title: Case Status Label
-- Skills: CASE WHEN
-- Tables: orders
-- Params: none
-- Level: intermediate

SELECT
    id,
    order_number,
    status,
    CASE status
        WHEN 'pending'   THEN 'Awaiting payment'
        WHEN 'paid'      THEN 'Paid'
        WHEN 'completed' THEN 'Fulfilled'
        WHEN 'cancelled' THEN 'Cancelled'
        ELSE 'Unknown'
    END AS status_label
FROM orders
ORDER BY order_date DESC
LIMIT 100;
