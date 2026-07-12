-- ID: I04
-- Title: Products Category Brand
-- Skills: multi JOIN
-- Tables: products, categories, brands
-- Params: none
-- Level: intermediate

SELECT
    p.sku,
    p.name AS product_name,
    p.unit_price,
    c.name AS category_name,
    b.name AS brand_name
FROM products p
INNER JOIN categories c ON c.id = p.category_id
LEFT JOIN brands b ON b.id = p.brand_id
WHERE p.deleted_at IS NULL
ORDER BY p.name
LIMIT 100;
