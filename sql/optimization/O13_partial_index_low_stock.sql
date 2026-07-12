-- ID: O13
-- Title: Partial Index Low Stock
-- Skills: partial index
-- Tables: inventory
-- Params: none
-- Level: optimization

-- Index: ix_inventory_low_stock WHERE quantity_on_hand <= reorder_level
EXPLAIN (ANALYZE, BUFFERS)
SELECT store_id, product_id, quantity_on_hand, reorder_level
FROM inventory
WHERE quantity_on_hand <= reorder_level
ORDER BY quantity_on_hand;
