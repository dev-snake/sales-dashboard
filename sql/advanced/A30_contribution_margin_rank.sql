-- ID: A30
-- Title: Contribution Margin Rank
-- Skills: profit window
-- Tables: orders, order_items, products
-- Params: none
-- Level: advanced

WITH product_profit AS (
    SELECT
        p.sku,
        p.name,
        SUM(oi.line_total) AS revenue,
        SUM(oi.quantity * oi.unit_cost) AS cogs,
        SUM(oi.line_total) - SUM(oi.quantity * oi.unit_cost) AS gross_profit
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
    cogs,
    gross_profit,
    RANK() OVER (ORDER BY gross_profit DESC) AS profit_rank
FROM product_profit
ORDER BY profit_rank
LIMIT 50;
