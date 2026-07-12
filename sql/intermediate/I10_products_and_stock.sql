-- ID: I10
-- Title: Products And Stock
-- Skills: LEFT JOIN
-- Tables: products, inventory
-- Params: none
-- Level: intermediate

SELECT
    p.sku,
    p.name,
    i.store_id,
    i.quantity_on_hand,
    i.reorder_level
FROM products p
LEFT JOIN inventory i ON i.product_id = p.id
WHERE p.deleted_at IS NULL
ORDER BY p.sku, i.store_id
LIMIT 200;
