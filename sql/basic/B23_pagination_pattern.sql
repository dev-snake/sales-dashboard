-- ID: B23
-- Title: Pagination Pattern
-- Skills: LIMIT OFFSET
-- Tables: products
-- Params: see comments in query
-- Level: basic

-- Page 2, size 20 (0-based offset = (page-1)*size)
SELECT id, sku, name, unit_price
FROM products
WHERE deleted_at IS NULL
ORDER BY id
LIMIT 20 OFFSET 20;
