-- ID: I09
-- Title: Stores Without Employees
-- Skills: LEFT JOIN anti-join
-- Tables: stores, employees
-- Params: none
-- Level: intermediate

SELECT
    s.id,
    s.code,
    s.name
FROM stores s
LEFT JOIN employees e ON e.store_id = s.id AND e.deleted_at IS NULL
WHERE e.id IS NULL
  AND s.deleted_at IS NULL;
