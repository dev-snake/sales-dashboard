-- ID: A08
-- Title: Row Number Products By Price
-- Skills: ROW_NUMBER
-- Tables: products
-- Params: none
-- Level: advanced

SELECT
    sku,
    name,
    unit_price,
    ROW_NUMBER() OVER (ORDER BY unit_price DESC) AS price_rank
FROM products
WHERE deleted_at IS NULL
ORDER BY price_rank
LIMIT 50;
