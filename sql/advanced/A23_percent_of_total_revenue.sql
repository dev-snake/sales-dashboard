-- ID: A23
-- Title: Percent Of Total Revenue
-- Skills: SUM / SUM OVER
-- Tables: orders, order_items, products
-- Params: none
-- Level: advanced

WITH product_rev AS (
    SELECT
        p.sku,
        p.name,
        SUM(oi.line_total) AS revenue
    FROM order_items oi
    INNER JOIN orders o ON o.id = oi.order_id
    INNER JOIN products p ON p.id = oi.product_id
    WHERE o.status IN ('paid', 'completed')
    GROUP BY p.sku, p.name
)
SELECT
    sku,
    name,
    revenue,
    ROUND(100.0 * revenue / SUM(revenue) OVER (), 4) AS pct_of_total
FROM product_rev
ORDER BY revenue DESC
LIMIT 50;
