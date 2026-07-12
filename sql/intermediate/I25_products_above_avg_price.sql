-- ID: I25
-- Title: Products Above Avg Price
-- Skills: scalar subquery
-- Tables: products
-- Params: none
-- Level: intermediate

SELECT id, sku, name, unit_price
FROM products
WHERE deleted_at IS NULL
  AND unit_price > (SELECT AVG(unit_price) FROM products WHERE deleted_at IS NULL)
ORDER BY unit_price DESC;
