-- ID: A11
-- Title: Dense Rank Employees
-- Skills: DENSE_RANK
-- Tables: orders, order_items, employees
-- Params: none
-- Level: advanced

WITH emp_rev AS (
    SELECT
        e.id,
        e.code,
        e.first_name || ' ' || e.last_name AS employee_name,
        SUM(oi.line_total) AS revenue
    FROM employees e
    INNER JOIN orders o ON o.employee_id = e.id
    INNER JOIN order_items oi ON oi.order_id = o.id
    WHERE o.status IN ('paid', 'completed')
    GROUP BY e.id, e.code, e.first_name, e.last_name
)
SELECT
    code,
    employee_name,
    revenue,
    DENSE_RANK() OVER (ORDER BY revenue DESC) AS dense_rank
FROM emp_rev
ORDER BY dense_rank;
