-- ID: A32
-- Title: Promo Vs Nonpromo Aov
-- Skills: CASE aggregate
-- Tables: orders
-- Params: none
-- Level: advanced

SELECT
    CASE WHEN promotion_id IS NULL THEN 'no_promo' ELSE 'with_promo' END AS promo_flag,
    COUNT(*) AS order_count,
    AVG(total_amount) AS aov,
    SUM(total_amount) AS total_sales
FROM orders
WHERE status IN ('paid', 'completed')
GROUP BY 1
ORDER BY 1;
