-- ID: R27
-- Title: New Vs Returning Customers
-- Skills: monthly
-- Tables: orders, customers
-- Params: :start_date, :end_date optional (see comments)
-- Level: reporting

WITH first_order AS (
    SELECT customer_id, MIN(order_date)::date AS first_date
    FROM orders
    WHERE status IN ('paid', 'completed')
    GROUP BY customer_id
),
monthly_buyers AS (
    SELECT
        DATE_TRUNC('month', o.order_date) AS month_key,
        o.customer_id,
        MIN(o.order_date)::date AS month_first_order
    FROM orders o
    WHERE o.status IN ('paid', 'completed')
    GROUP BY DATE_TRUNC('month', o.order_date), o.customer_id
)
SELECT
    m.month_key,
    COUNT(*) FILTER (
        WHERE DATE_TRUNC('month', f.first_date) = m.month_key
    ) AS new_customers,
    COUNT(*) FILTER (
        WHERE DATE_TRUNC('month', f.first_date) < m.month_key
    ) AS returning_customers
FROM monthly_buyers m
INNER JOIN first_order f ON f.customer_id = m.customer_id
GROUP BY m.month_key
ORDER BY m.month_key;
