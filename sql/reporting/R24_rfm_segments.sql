-- ID: R24
-- Title: Rfm Segments
-- Skills: RFM segments
-- Tables: orders, order_items, customers
-- Params: none
-- Level: reporting

WITH base AS (
    SELECT
        c.id AS customer_id,
        c.code AS customer_code,
        (CURRENT_DATE - MAX(o.order_date)::date) AS recency_days,
        COUNT(DISTINCT o.id) AS frequency,
        SUM(oi.line_total) AS monetary
    FROM customers c
    INNER JOIN orders o ON o.customer_id = c.id
    INNER JOIN order_items oi ON oi.order_id = o.id
    WHERE o.status IN ('paid', 'completed')
    GROUP BY c.id, c.code
),
scored AS (
    SELECT
        customer_code,
        recency_days,
        frequency,
        monetary,
        -- Lower recency_days is better => higher r_score via ORDER BY recency_days DESC in NTILE
        NTILE(5) OVER (ORDER BY recency_days DESC) AS r_score,
        NTILE(5) OVER (ORDER BY frequency ASC) AS f_score,
        NTILE(5) OVER (ORDER BY monetary ASC) AS m_score
    FROM base
)
SELECT
    customer_code,
    recency_days,
    frequency,
    monetary,
    r_score,
    f_score,
    m_score,
    CASE
        WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
        WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 3 THEN 'Loyal'
        WHEN r_score >= 4 AND f_score <= 2 THEN 'New / Promising'
        WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk'
        WHEN r_score <= 2 AND f_score <= 2 AND m_score <= 2 THEN 'Hibernating'
        ELSE 'Need Attention'
    END AS segment
FROM scored
ORDER BY monetary DESC
LIMIT 200;
