-- ID: R07
-- Title: Top Employees By Revenue
-- Skills: Top N
-- Tables: orders, order_items, employees
-- Params: :start_date, :end_date optional (see comments)
-- Level: reporting

SELECT
    e.code AS employee_code,
    e.first_name || ' ' || e.last_name AS employee_name,
    COUNT(DISTINCT o.id) AS order_count,
    SUM(oi.line_total) AS revenue
FROM order_items oi
INNER JOIN orders o ON o.id = oi.order_id
INNER JOIN employees e ON e.id = o.employee_id
WHERE o.status IN ('paid', 'completed')
GROUP BY e.code, e.first_name, e.last_name
ORDER BY revenue DESC
LIMIT 20;
