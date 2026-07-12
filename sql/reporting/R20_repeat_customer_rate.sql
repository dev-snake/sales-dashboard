-- ID: R20
-- Title: Repeat Customer Rate
-- Skills: KPI
-- Tables: orders, customers
-- Params: :start_date, :end_date optional (see comments)
-- Level: reporting

WITH buyers AS (
    SELECT
        customer_id,
        COUNT(*) AS order_count
    FROM orders
    WHERE status IN ('paid', 'completed')
    GROUP BY customer_id
)
SELECT
    COUNT(*) AS total_buyers,
    COUNT(*) FILTER (WHERE order_count >= 2) AS repeat_buyers,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE order_count >= 2) / NULLIF(COUNT(*), 0),
        2
    ) AS repeat_customer_rate_pct
FROM buyers;
