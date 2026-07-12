-- ID: A31
-- Title: Inventory Vs Sales Velocity
-- Skills: multi CTE + window
-- Tables: inventory, order_items, orders, products
-- Params: none
-- Level: advanced

WITH sales_30d AS (
    SELECT
        oi.product_id,
        SUM(oi.quantity) AS qty_sold_30d
    FROM order_items oi
    INNER JOIN orders o ON o.id = oi.order_id
    WHERE o.status IN ('paid', 'completed')
      AND o.order_date >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY oi.product_id
),
stock AS (
    SELECT product_id, SUM(quantity_on_hand) AS on_hand
    FROM inventory
    GROUP BY product_id
)
SELECT
    p.sku,
    p.name,
    COALESCE(s.on_hand, 0) AS on_hand,
    COALESCE(v.qty_sold_30d, 0) AS qty_sold_30d,
    CASE
        WHEN COALESCE(v.qty_sold_30d, 0) = 0 THEN NULL
        ELSE ROUND(COALESCE(s.on_hand, 0)::numeric / v.qty_sold_30d, 2)
    END AS days_of_cover_proxy
FROM products p
LEFT JOIN stock s ON s.product_id = p.id
LEFT JOIN sales_30d v ON v.product_id = p.id
WHERE p.deleted_at IS NULL
ORDER BY qty_sold_30d DESC NULLS LAST
LIMIT 100;
