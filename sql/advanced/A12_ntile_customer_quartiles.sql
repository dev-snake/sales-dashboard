-- ID: A12
-- Title: Ntile Customer Quartiles
-- Skills: NTILE
-- Tables: orders, order_items, customers
-- Params: none
-- Level: advanced

WITH cust_monetary AS (
    SELECT
        c.id,
        c.code,
        SUM(oi.line_total) AS monetary
    FROM customers c
    INNER JOIN orders o ON o.customer_id = c.id
    INNER JOIN order_items oi ON oi.order_id = o.id
    WHERE o.status IN ('paid', 'completed')
    GROUP BY c.id, c.code
)
SELECT
    code,
    monetary,
    NTILE(4) OVER (ORDER BY monetary DESC) AS monetary_quartile
FROM cust_monetary
ORDER BY monetary DESC;
