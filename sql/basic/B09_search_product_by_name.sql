-- ID: B09
-- Title: Search Product By Name
-- Skills: LIKE / ILIKE
-- Tables: products
-- Params: see comments in query
-- Level: basic

-- Param: keyword
SELECT id, sku, name, unit_price
FROM products
WHERE name ILIKE '%Blue%'
  AND deleted_at IS NULL;
