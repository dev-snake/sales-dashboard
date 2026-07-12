-- ID: B02
-- Title: Customers In City
-- Skills: WHERE
-- Tables: customers
-- Params: see comments in query
-- Level: basic

-- Param: city name
SELECT id, code, first_name, last_name, email, city
FROM customers
WHERE city = 'Ha Noi'
  AND deleted_at IS NULL;
