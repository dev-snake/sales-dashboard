-- ID: I05
-- Title: Employees With Store
-- Skills: INNER JOIN
-- Tables: employees, stores
-- Params: none
-- Level: intermediate

SELECT
    e.code AS employee_code,
    e.first_name || ' ' || e.last_name AS employee_name,
    e.job_title,
    s.code AS store_code,
    s.name AS store_name
FROM employees e
INNER JOIN stores s ON s.id = e.store_id
WHERE e.deleted_at IS NULL
ORDER BY s.code, e.code;
