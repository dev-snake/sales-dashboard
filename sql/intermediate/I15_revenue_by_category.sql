-- ID: I15
-- Title: Revenue By Category
-- Skills: GROUP BY
-- Tables: orders, order_items, products, categories
-- Params: none
-- Level: intermediate

SELECT
    c.id AS category_id,
    c.name AS category_name,
    SUM(oi.line_total) AS revenue
FROM order_items oi
INNER JOIN orders o ON o.id = oi.order_id
INNER JOIN products p ON p.id = oi.product_id
INNER JOIN categories c ON c.id = p.category_id
WHERE o.status IN ('paid', 'completed')
GROUP BY c.id, c.name
ORDER BY revenue DESC;
