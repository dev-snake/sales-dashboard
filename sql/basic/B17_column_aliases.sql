-- ID: B17
-- Title: Column Aliases
-- Skills: AS
-- Tables: products
-- Params: see comments in query
-- Level: basic

SELECT
    id            AS product_id,
    sku           AS stock_keeping_unit,
    name          AS product_name,
    unit_price    AS list_price,
    cost_price    AS unit_cost
FROM products
WHERE deleted_at IS NULL
LIMIT 50;
