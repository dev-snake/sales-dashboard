-- ID: R10
-- Title: Sales By Brand
-- Skills: breakdown
-- Tables: orders, order_items, products, brands
-- Params: :start_date, :end_date optional (see comments)
-- Level: reporting

SELECT
    COALESCE(b.name, 'Unknown') AS brand_name,
    SUM(oi.line_total) AS revenue,
    SUM(oi.quantity) AS units
FROM order_items oi
INNER JOIN orders o ON o.id = oi.order_id
INNER JOIN products p ON p.id = oi.product_id
LEFT JOIN brands b ON b.id = p.brand_id
WHERE o.status IN ('paid', 'completed')
GROUP BY COALESCE(b.name, 'Unknown')
ORDER BY revenue DESC;
