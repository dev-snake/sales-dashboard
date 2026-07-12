-- ID: R22
-- Title: Pareto 80 20
-- Skills: Pareto
-- Tables: orders, order_items, products
-- Params: :start_date, :end_date optional (see comments)
-- Level: reporting

WITH product_rev AS (
    SELECT
        p.sku,
        SUM(oi.line_total) AS revenue
    FROM order_items oi
    INNER JOIN orders o ON o.id = oi.order_id
    INNER JOIN products p ON p.id = oi.product_id
    WHERE o.status IN ('paid', 'completed')
    GROUP BY p.sku
),
ranked AS (
    SELECT
        sku,
        revenue,
        SUM(revenue) OVER (ORDER BY revenue DESC ROWS UNBOUNDED PRECEDING) AS cum_revenue,
        SUM(revenue) OVER () AS total_revenue,
        COUNT(*) OVER () AS product_count,
        ROW_NUMBER() OVER (ORDER BY revenue DESC) AS rn
    FROM product_rev
)
SELECT
    MIN(rn) FILTER (
        WHERE cum_revenue / NULLIF(total_revenue, 0) >= 0.80
    ) AS products_for_80pct_revenue,
    MAX(product_count) AS total_products,
    ROUND(
        100.0 * MIN(rn) FILTER (
            WHERE cum_revenue / NULLIF(total_revenue, 0) >= 0.80
        ) / NULLIF(MAX(product_count), 0),
        2
    ) AS pct_products_for_80pct_revenue
FROM ranked;
