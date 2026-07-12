-- ID: B01
-- Title: List Active Products
-- Skills: SELECT
-- Tables: products
-- Params: see comments in query
-- Level: basic

SELECT id, sku, name, unit_price
FROM products
WHERE is_active = TRUE
  AND deleted_at IS NULL
ORDER BY name;
