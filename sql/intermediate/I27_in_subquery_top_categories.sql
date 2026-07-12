-- ID: I27
-- Title: In Subquery Top Categories
-- Skills: IN subquery
-- Tables: products, categories, order_items, orders
-- Params: none
-- Level: intermediate

SELECT p.sku, p.name, c.name AS category_name
FROM products p
INNER JOIN categories c ON c.id = p.category_id
WHERE c.id IN (
    SELECT p2.category_id
    FROM order_items oi
    INNER JOIN orders o ON o.id = oi.order_id
    INNER JOIN products p2 ON p2.id = oi.product_id
    WHERE o.status IN ('paid', 'completed')
    GROUP BY p2.category_id
    ORDER BY SUM(oi.line_total) DESC
    LIMIT 5
)
ORDER BY c.name, p.name;
