-- ID: A24
-- Title: Cume Dist Products
-- Skills: CUME_DIST
-- Tables: orders, order_items, products
-- Params: none
-- Level: advanced

WITH product_rev AS (
    SELECT
        p.sku,
        SUM(oi.line_total) AS revenue
    FROM order_items oi
    INNER JOIN orders o ON o.id = oi.order_id
    INNER JOIN products p ON p.id = oi.product_id
    WHERE o.status IN ('paid', 'completed')
    GROUP BY p.sku
)
SELECT
    sku,
    revenue,
    CUME_DIST() OVER (ORDER BY revenue) AS cume_dist
FROM product_rev
ORDER BY revenue DESC
LIMIT 50;
