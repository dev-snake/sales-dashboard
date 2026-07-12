-- ID: I26
-- Title: Orders Above Avg Total
-- Skills: scalar subquery
-- Tables: orders
-- Params: none
-- Level: intermediate

SELECT id, order_number, total_amount, status
FROM orders
WHERE status IN ('paid', 'completed')
  AND total_amount > (
        SELECT AVG(total_amount)
        FROM orders
        WHERE status IN ('paid', 'completed')
      )
ORDER BY total_amount DESC;
