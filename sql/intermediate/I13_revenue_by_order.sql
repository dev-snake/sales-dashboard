-- ID: I13
-- Title: Revenue By Order
-- Skills: GROUP BY
-- Tables: orders, order_items
-- Params: none
-- Level: intermediate

SELECT
    o.id AS order_id,
    o.order_number,
    SUM(oi.line_total) AS revenue
FROM orders o
INNER JOIN order_items oi ON oi.order_id = o.id
WHERE o.status IN ('paid', 'completed')
GROUP BY o.id, o.order_number
ORDER BY revenue DESC
LIMIT 100;
