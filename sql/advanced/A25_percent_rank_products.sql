-- ID: A25
-- Title: Percent Rank Products
-- Skills: PERCENT_RANK
-- Tables: products
-- Params: none
-- Level: advanced

SELECT
    sku,
    name,
    unit_price,
    PERCENT_RANK() OVER (ORDER BY unit_price) AS pct_rank
FROM products
WHERE deleted_at IS NULL
ORDER BY unit_price DESC
LIMIT 50;
