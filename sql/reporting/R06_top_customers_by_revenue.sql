-- ID: R06
-- Title: Top Customers By Revenue
-- Skills: Top N
-- Tables: orders, order_items, customers
-- Params: :start_date, :end_date optional (see comments)
-- Level: reporting

SELECT
    c.code AS customer_code,
    c.first_name || ' ' || c.last_name AS customer_name,
    COUNT(DISTINCT o.id) AS order_count,
    SUM(oi.line_total) AS revenue
FROM order_items oi
INNER JOIN orders o ON o.id = oi.order_id
INNER JOIN customers c ON c.id = o.customer_id
WHERE o.status IN ('paid', 'completed')
GROUP BY c.code, c.first_name, c.last_name
ORDER BY revenue DESC
LIMIT 20;
