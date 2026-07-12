-- ID: B13
-- Title: Orders Selected Stores
-- Skills: IN
-- Tables: orders
-- Params: see comments in query
-- Level: basic

-- Param: store id list
SELECT id, order_number, store_id, total_amount
FROM orders
WHERE store_id IN (1, 2, 3)
ORDER BY order_date DESC;
