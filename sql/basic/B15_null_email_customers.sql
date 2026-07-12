-- ID: B15
-- Title: Null Email Customers
-- Skills: IS NULL
-- Tables: customers
-- Params: see comments in query
-- Level: basic

SELECT id, code, first_name, last_name, phone
FROM customers
WHERE email IS NULL
  AND deleted_at IS NULL;
