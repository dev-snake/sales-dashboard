-- ID: R09
-- Title: Sales By Category
-- Skills: breakdown
-- Tables: orders, order_items, products, categories
-- Params: :start_date, :end_date optional (see comments)
-- Level: reporting

SELECT
    c.name AS category_name,
    SUM(oi.line_total) AS revenue,
    SUM(oi.quantity) AS units
FROM order_items oi
INNER JOIN orders o ON o.id = oi.order_id
INNER JOIN products p ON p.id = oi.product_id
INNER JOIN categories c ON c.id = p.category_id
WHERE o.status IN ('paid', 'completed')
GROUP BY c.name
ORDER BY revenue DESC;
