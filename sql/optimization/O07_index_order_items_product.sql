-- ID: O07
-- Title: Index Order Items Product
-- Skills: index
-- Tables: order_items, products
-- Params: none
-- Level: optimization

-- Index: ix_order_items_product_id — top products path
EXPLAIN (ANALYZE, BUFFERS)
SELECT product_id, SUM(line_total) AS revenue
FROM order_items
WHERE product_id = 1
GROUP BY product_id;
