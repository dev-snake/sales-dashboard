-- ID: I11
-- Title: Right Join Demo
-- Skills: RIGHT JOIN
-- Tables: inventory, stores
-- Params: none
-- Level: intermediate

-- Demo: every store with optional inventory rows
SELECT
    s.code AS store_code,
    s.name AS store_name,
    i.product_id,
    i.quantity_on_hand
FROM inventory i
RIGHT JOIN stores s ON s.id = i.store_id
WHERE s.deleted_at IS NULL
ORDER BY s.code
LIMIT 200;
