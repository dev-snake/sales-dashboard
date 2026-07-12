-- ID: A03
-- Title: Filter Cte Then Join
-- Skills: CTE hygiene
-- Tables: orders, customers, stores
-- Params: none
-- Level: advanced

WITH recent_orders AS (
    SELECT id, customer_id, store_id, order_number, total_amount, order_date
    FROM orders
    WHERE status IN ('paid', 'completed')
      AND order_date >= CURRENT_DATE - INTERVAL '90 days'
)
SELECT
    ro.order_number,
    ro.order_date,
    ro.total_amount,
    c.code AS customer_code,
    s.code AS store_code
FROM recent_orders ro
INNER JOIN customers c ON c.id = ro.customer_id
INNER JOIN stores s ON s.id = ro.store_id
ORDER BY ro.order_date DESC;
