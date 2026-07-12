-- ID: B05
-- Title: Sort Products By Price
-- Skills: ORDER BY
-- Tables: products
-- Params: see comments in query
-- Level: basic

SELECT id, sku, name, unit_price
FROM products
WHERE deleted_at IS NULL
ORDER BY unit_price DESC;
