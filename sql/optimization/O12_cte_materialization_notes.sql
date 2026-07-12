-- ID: O12
-- Title: Cte Materialization Notes
-- Skills: CTE PG15+
-- Tables: orders, order_items
-- Params: none
-- Level: optimization

-- PG12+ may inline CTEs; PG12 introduced MATERIALIZED / NOT MATERIALIZED hints.
-- Compare plans:
-- WITH x AS MATERIALIZED (...) SELECT ...
-- WITH x AS NOT MATERIALIZED (...) SELECT ...
WITH monthly AS NOT MATERIALIZED (
    SELECT
        DATE_TRUNC('month', o.order_date) AS month_key,
        SUM(oi.line_total) AS revenue
    FROM order_items oi
    INNER JOIN orders o ON o.id = oi.order_id
    WHERE o.status IN ('paid', 'completed')
    GROUP BY 1
)
SELECT * FROM monthly ORDER BY month_key;
