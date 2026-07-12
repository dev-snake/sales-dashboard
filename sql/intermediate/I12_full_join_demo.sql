-- ID: I12
-- Title: Full Join Demo
-- Skills: FULL JOIN
-- Tables: products, inventory
-- Params: none
-- Level: intermediate

-- Demo matching product catalog vs inventory presence
SELECT
    p.sku,
    p.name AS product_name,
    i.store_id,
    i.quantity_on_hand
FROM products p
FULL JOIN inventory i ON i.product_id = p.id
ORDER BY COALESCE(p.sku, 'zzz')
LIMIT 200;
