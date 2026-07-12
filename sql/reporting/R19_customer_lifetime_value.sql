-- ID: R19
-- Title: Customer Lifetime Value
-- Skills: CLV
-- Tables: orders, order_items, customers
-- Params: :start_date, :end_date optional (see comments)
-- Level: reporting

SELECT
    c.code AS customer_code,
    c.first_name || ' ' || c.last_name AS customer_name,
    MIN(o.order_date) AS first_order_at,
    MAX(o.order_date) AS last_order_at,
    COUNT(DISTINCT o.id) AS order_count,
    SUM(oi.line_total) AS lifetime_revenue
FROM customers c
INNER JOIN orders o ON o.customer_id = c.id
INNER JOIN order_items oi ON oi.order_id = o.id
WHERE o.status IN ('paid', 'completed')
GROUP BY c.code, c.first_name, c.last_name
ORDER BY lifetime_revenue DESC
LIMIT 100;
