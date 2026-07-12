-- ID: R25
-- Title: Cohort Retention
-- Skills: Cohort
-- Tables: orders, customers
-- Params: :start_date, :end_date optional (see comments)
-- Level: reporting

WITH first_orders AS (
    SELECT
        customer_id,
        DATE_TRUNC('month', MIN(order_date)) AS cohort_month
    FROM orders
    WHERE status IN ('paid', 'completed')
    GROUP BY customer_id
),
activity AS (
    SELECT
        o.customer_id,
        DATE_TRUNC('month', o.order_date) AS activity_month
    FROM orders o
    WHERE o.status IN ('paid', 'completed')
    GROUP BY o.customer_id, DATE_TRUNC('month', o.order_date)
)
SELECT
    f.cohort_month,
    a.activity_month,
    (
        EXTRACT(YEAR FROM age(a.activity_month, f.cohort_month)) * 12
        + EXTRACT(MONTH FROM age(a.activity_month, f.cohort_month))
    )::int AS period_number,
    COUNT(DISTINCT a.customer_id) AS active_customers
FROM first_orders f
INNER JOIN activity a ON a.customer_id = f.customer_id
GROUP BY f.cohort_month, a.activity_month
ORDER BY f.cohort_month, period_number;
