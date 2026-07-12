-- ID: I28
-- Title: Exists Active Promo Orders
-- Skills: EXISTS
-- Tables: orders, promotions
-- Params: none
-- Level: intermediate

SELECT o.id, o.order_number, o.promotion_id, o.total_amount
FROM orders o
WHERE EXISTS (
    SELECT 1
    FROM promotions pr
    WHERE pr.id = o.promotion_id
      AND pr.is_active = TRUE
      AND pr.deleted_at IS NULL
)
ORDER BY o.order_date DESC
LIMIT 100;
