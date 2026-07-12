-- ID: I02
-- Title: Order Lines With Product
-- Skills: INNER JOIN
-- Tables: order_items, products
-- Params: none
-- Level: intermediate

SELECT
    oi.id AS order_item_id,
    oi.order_id,
    p.sku,
    p.name AS product_name,
    oi.quantity,
    oi.unit_price,
    oi.line_total
FROM order_items oi
INNER JOIN products p ON p.id = oi.product_id
LIMIT 100;
