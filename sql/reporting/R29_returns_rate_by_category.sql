-- ID: R29
-- Title: Returns Rate By Category
-- Skills: returns
-- Tables: returns, order_items, orders, products, categories
-- Params: :start_date, :end_date optional (see comments)
-- Level: reporting

WITH sold AS (
    SELECT p.category_id, SUM(oi.quantity) AS sold_qty
    FROM order_items oi
    INNER JOIN orders o ON o.id = oi.order_id
    INNER JOIN products p ON p.id = oi.product_id
    WHERE o.status IN ('paid', 'completed')
    GROUP BY p.category_id
),
ret AS (
    SELECT p.category_id, SUM(r.quantity) AS returned_qty
    FROM returns r
    INNER JOIN order_items oi ON oi.id = r.order_item_id
    INNER JOIN products p ON p.id = oi.product_id
    WHERE r.status IN ('approved', 'completed')
    GROUP BY p.category_id
)
SELECT
    c.name AS category_name,
    COALESCE(s.sold_qty, 0) AS sold_qty,
    COALESCE(rt.returned_qty, 0) AS returned_qty,
    ROUND(
        100.0 * COALESCE(rt.returned_qty, 0) / NULLIF(s.sold_qty, 0),
        2
    ) AS return_rate_pct
FROM categories c
LEFT JOIN sold s ON s.category_id = c.id
LEFT JOIN ret rt ON rt.category_id = c.id
WHERE c.deleted_at IS NULL
ORDER BY return_rate_pct DESC NULLS LAST;
