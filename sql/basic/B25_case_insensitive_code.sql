-- ID: B25
-- Title: Case Insensitive Code
-- Skills: UPPER/LOWER
-- Tables: products
-- Params: see comments in query
-- Level: basic

-- Param: sku text
SELECT id, sku, name, unit_price
FROM products
WHERE UPPER(sku) = UPPER('sku-001-001-000001')
  AND deleted_at IS NULL;
