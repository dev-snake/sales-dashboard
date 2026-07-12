-- ID: I07
-- Title: Products Never Sold
-- Skills: LEFT JOIN anti-join
-- Tables: products, order_items
-- Params: none
-- Level: intermediate

SELECT
    p.id,
    p.sku,
    p.name,
    p.unit_price
FROM products p
LEFT JOIN order_items oi ON oi.product_id = p.id
WHERE oi.id IS NULL
  AND p.deleted_at IS NULL
ORDER BY p.sku;
