-- ID: A33
-- Title: Return Rate By Product
-- Skills: CTE returns/sales
-- Tables: returns, order_items, orders, products
-- Params: none
-- Level: advanced

WITH sold AS (
    SELECT oi.product_id, SUM(oi.quantity) AS sold_qty
    FROM order_items oi
    INNER JOIN orders o ON o.id = oi.order_id
    WHERE o.status IN ('paid', 'completed')
    GROUP BY oi.product_id
),
ret AS (
    SELECT oi.product_id, SUM(r.quantity) AS returned_qty
    FROM returns r
    INNER JOIN order_items oi ON oi.id = r.order_item_id
    WHERE r.status IN ('approved', 'completed')
    GROUP BY oi.product_id
)
SELECT
    p.sku,
    p.name,
    COALESCE(s.sold_qty, 0) AS sold_qty,
    COALESCE(rt.returned_qty, 0) AS returned_qty,
    ROUND(
        100.0 * COALESCE(rt.returned_qty, 0) / NULLIF(s.sold_qty, 0),
        2
    ) AS return_rate_pct
FROM products p
LEFT JOIN sold s ON s.product_id = p.id
LEFT JOIN ret rt ON rt.product_id = p.id
WHERE p.deleted_at IS NULL
ORDER BY return_rate_pct DESC NULLS LAST
LIMIT 50;
