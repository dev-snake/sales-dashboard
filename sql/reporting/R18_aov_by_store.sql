-- ID: R18
-- Title: Aov By Store
-- Skills: KPI breakdown
-- Tables: orders, order_items, stores
-- Params: :start_date, :end_date optional (see comments)
-- Level: reporting

SELECT
    s.code AS store_code,
    s.name AS store_name,
    SUM(oi.line_total) AS revenue,
    COUNT(DISTINCT o.id) AS order_count,
    SUM(oi.line_total) / NULLIF(COUNT(DISTINCT o.id), 0) AS aov
FROM order_items oi
INNER JOIN orders o ON o.id = oi.order_id
INNER JOIN stores s ON s.id = o.store_id
WHERE o.status IN ('paid', 'completed')
GROUP BY s.code, s.name
ORDER BY aov DESC;
