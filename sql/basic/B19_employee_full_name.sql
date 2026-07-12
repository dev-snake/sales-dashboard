-- ID: B19
-- Title: Employee Full Name
-- Skills: string concat
-- Tables: employees
-- Params: see comments in query
-- Level: basic

SELECT
    id,
    code,
    first_name || ' ' || last_name AS full_name,
    job_title
FROM employees
WHERE deleted_at IS NULL
ORDER BY full_name;
