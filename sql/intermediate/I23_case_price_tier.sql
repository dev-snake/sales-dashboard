-- ID: I23
-- Title: Case Price Tier
-- Skills: CASE WHEN
-- Tables: products
-- Params: none
-- Level: intermediate

SELECT
    sku,
    name,
    unit_price,
    CASE
        WHEN unit_price < 100000 THEN 'budget'
        WHEN unit_price < 1000000 THEN 'mid'
        ELSE 'premium'
    END AS price_tier
FROM products
WHERE deleted_at IS NULL
ORDER BY unit_price;
