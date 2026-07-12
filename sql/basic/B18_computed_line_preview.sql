-- ID: B18
-- Title: Computed Line Preview
-- Skills: arithmetic
-- Tables: order_items
-- Params: see comments in query
-- Level: basic

SELECT
    id,
    order_id,
    product_id,
    quantity,
    unit_price,
    quantity * unit_price AS gross_before_discount,
    discount_amount,
    line_total
FROM order_items
LIMIT 100;
