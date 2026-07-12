-- ID: B08
-- Title: Distinct Customer Cities
-- Skills: DISTINCT
-- Tables: customers
-- Params: see comments in query
-- Level: basic

SELECT DISTINCT city
FROM customers
WHERE city IS NOT NULL
  AND deleted_at IS NULL
ORDER BY city;
