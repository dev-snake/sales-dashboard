-- ID: A05
-- Title: Employee Hierarchy
-- Skills: Recursive CTE
-- Tables: employees
-- Params: none
-- Level: advanced

WITH RECURSIVE org AS (
    SELECT
        id, code, first_name, last_name, manager_id, store_id, 1 AS depth,
        first_name || ' ' || last_name AS path
    FROM employees
    WHERE manager_id IS NULL
      AND deleted_at IS NULL
    UNION ALL
    SELECT
        e.id, e.code, e.first_name, e.last_name, e.manager_id, e.store_id,
        org.depth + 1,
        org.path || ' > ' || e.first_name || ' ' || e.last_name
    FROM employees e
    INNER JOIN org ON e.manager_id = org.id
    WHERE e.deleted_at IS NULL
)
SELECT id, code, first_name, last_name, manager_id, depth, path
FROM org
ORDER BY path;
