-- ID: B12
-- Title: Products Price Band
-- Skills: BETWEEN
-- Tables: products
-- Params: see comments in query
-- Level: basic

SELECT id, sku, name, unit_price
FROM products
WHERE unit_price BETWEEN 100000 AND 500000
  AND deleted_at IS NULL
ORDER BY unit_price;
