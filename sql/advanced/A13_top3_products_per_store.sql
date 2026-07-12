-- ID: A13
-- Title: Top3 Products Per Store
-- Skills: PARTITION store
-- Tables: orders, order_items, products, stores
-- Params: none
-- Level: advanced

WITH store_product AS (
    SELECT
        s.id AS store_id,
        s.code AS store_code,
        p.sku,
        p.name AS product_name,
        SUM(oi.line_total) AS revenue,
        ROW_NUMBER() OVER (
            PARTITION BY s.id
            ORDER BY SUM(oi.line_total) DESC
        ) AS rn
    FROM order_items oi
    INNER JOIN orders o ON o.id = oi.order_id
    INNER JOIN products p ON p.id = oi.product_id
    INNER JOIN stores s ON s.id = o.store_id
    WHERE o.status IN ('paid', 'completed')
    GROUP BY s.id, s.code, p.sku, p.name
)
SELECT store_code, sku, product_name, revenue, rn
FROM store_product
WHERE rn <= 3
ORDER BY store_code, rn;
