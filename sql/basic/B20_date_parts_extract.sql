-- ID: B20
-- Title: Date Parts Extract
-- Skills: EXTRACT
-- Tables: orders
-- Params: see comments in query
-- Level: basic

SELECT
    id,
    order_number,
    EXTRACT(YEAR  FROM order_date) AS order_year,
    EXTRACT(MONTH FROM order_date) AS order_month,
    EXTRACT(DAY   FROM order_date) AS order_day
FROM orders
ORDER BY order_date DESC
LIMIT 100;
