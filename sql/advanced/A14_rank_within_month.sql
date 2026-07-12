-- ID: A14
-- Title: Rank Within Month
-- Skills: PARTITION year month
-- Tables: orders, order_items, products
-- Params: none
-- Level: advanced

WITH monthly_product AS (
    SELECT
        EXTRACT(YEAR FROM o.order_date)::int AS yr,
        EXTRACT(MONTH FROM o.order_date)::int AS mo,
        p.sku,
        SUM(oi.line_total) AS revenue
    FROM order_items oi
    INNER JOIN orders o ON o.id = oi.order_id
    INNER JOIN products p ON p.id = oi.product_id
    WHERE o.status IN ('paid', 'completed')
    GROUP BY 1, 2, p.sku
)
SELECT
    yr,
    mo,
    sku,
    revenue,
    RANK() OVER (PARTITION BY yr, mo ORDER BY revenue DESC) AS month_rank
FROM monthly_product
ORDER BY yr, mo, month_rank
LIMIT 200;
