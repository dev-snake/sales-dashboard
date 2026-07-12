-- ID: B21
-- Title: Active Stores
-- Skills: boolean filter
-- Tables: stores
-- Params: see comments in query
-- Level: basic

SELECT id, code, name, city, is_active
FROM stores
WHERE is_active = TRUE
  AND deleted_at IS NULL;
