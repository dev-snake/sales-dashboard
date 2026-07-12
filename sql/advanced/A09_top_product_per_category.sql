-- ID: A09
-- Title: Top Product Per Category
-- Skills: ROW_NUMBER PARTITION
-- Tables: products, categories
-- Params: none
-- Level: advanced

WITH ranked AS (
    SELECT
        p.id,
        p.sku,
        p.name,
        p.unit_price,
        c.name AS category_name,
        ROW_NUMBER() OVER (
            PARTITION BY p.category_id
            ORDER BY p.unit_price DESC
        ) AS rn
    FROM products p
    INNER JOIN categories c ON c.id = p.category_id
    WHERE p.deleted_at IS NULL
)
SELECT sku, name, unit_price, category_name
FROM ranked
WHERE rn = 1
ORDER BY category_name;
