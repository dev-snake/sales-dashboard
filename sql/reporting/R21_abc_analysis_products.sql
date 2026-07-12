-- ID: R21
-- Title: Abc Analysis Products
-- Skills: ABC cumulative
-- Tables: orders, order_items, products
-- Params: :start_date, :end_date optional (see comments)
-- Level: reporting

WITH product_rev AS (
    SELECT
        p.id,
        p.sku,
        p.name,
        SUM(oi.line_total) AS revenue
    FROM order_items oi
    INNER JOIN orders o ON o.id = oi.order_id
    INNER JOIN products p ON p.id = oi.product_id
    WHERE o.status IN ('paid', 'completed')
    GROUP BY p.id, p.sku, p.name
),
ranked AS (
    SELECT
        *,
        SUM(revenue) OVER (ORDER BY revenue DESC
            ROWS UNBOUNDED PRECEDING) AS cum_revenue,
        SUM(revenue) OVER () AS total_revenue
    FROM product_rev
)
SELECT
    sku,
    name,
    revenue,
    ROUND(100.0 * cum_revenue / NULLIF(total_revenue, 0), 2) AS cum_revenue_pct,
    CASE
        WHEN cum_revenue / NULLIF(total_revenue, 0) <= 0.80 THEN 'A'
        WHEN cum_revenue / NULLIF(total_revenue, 0) <= 0.95 THEN 'B'
        ELSE 'C'
    END AS abc_class
FROM ranked
ORDER BY revenue DESC;
