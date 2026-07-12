-- ID: B16
-- Title: Nonnull Phone Customers
-- Skills: IS NOT NULL
-- Tables: customers
-- Params: see comments in query
-- Level: basic

SELECT id, code, first_name, last_name, phone
FROM customers
WHERE phone IS NOT NULL
  AND deleted_at IS NULL;
