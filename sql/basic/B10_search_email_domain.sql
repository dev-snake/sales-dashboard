-- ID: B10
-- Title: Search Email Domain
-- Skills: LIKE
-- Tables: customers
-- Params: see comments in query
-- Level: basic

SELECT id, code, email
FROM customers
WHERE email ILIKE '%@example.com'
  AND deleted_at IS NULL;
