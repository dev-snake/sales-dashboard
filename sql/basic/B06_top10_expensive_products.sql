-- ID: B06
-- Title: Top10 Expensive Products
-- Skills: ORDER BY, LIMIT
-- Tables: products
-- Params: see comments in query
-- Level: basic

SELECT id, sku, name, unit_price
FROM products
WHERE deleted_at IS NULL
ORDER BY unit_price DESC
LIMIT 10;
