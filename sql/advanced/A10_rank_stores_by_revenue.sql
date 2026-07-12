-- ID: A10
-- Title: Rank Stores By Revenue
-- Skills: RANK
-- Tables: orders, order_items, stores
-- Params: none
-- Level: advanced

WITH store_rev AS (
    SELECT
        s.id,
        s.code,
        s.name,
        SUM(oi.line_total) AS revenue
    FROM stores s
    INNER JOIN orders o ON o.store_id = s.id
    INNER JOIN order_items oi ON oi.order_id = o.id
    WHERE o.status IN ('paid', 'completed')
    GROUP BY s.id, s.code, s.name
)
SELECT
    code,
    name,
    revenue,
    RANK() OVER (ORDER BY revenue DESC) AS revenue_rank
FROM store_rev
ORDER BY revenue_rank;
