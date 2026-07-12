-- ID: I19
-- Title: Categories With Many Products
-- Skills: HAVING
-- Tables: products, categories
-- Params: none
-- Level: intermediate

-- Param: min_products (example 5)
SELECT
    c.name AS category_name,
    COUNT(p.id) AS product_count
FROM categories c
INNER JOIN products p ON p.category_id = c.id AND p.deleted_at IS NULL
WHERE c.deleted_at IS NULL
GROUP BY c.name
HAVING COUNT(p.id) > 5
ORDER BY product_count DESC;
