-- ID: R16
-- Title: Sales By Day Of Week
-- Skills: calendar join
-- Tables: orders, order_items, calendar
-- Params: :start_date, :end_date optional (see comments)
-- Level: reporting

SELECT
    cal.day_of_week,
    cal.day_name,
    SUM(oi.line_total) AS revenue,
    COUNT(DISTINCT o.id) AS order_count
FROM order_items oi
INNER JOIN orders o ON o.id = oi.order_id
INNER JOIN calendar cal ON cal.full_date = o.order_date::date
WHERE o.status IN ('paid', 'completed')
GROUP BY cal.day_of_week, cal.day_name
ORDER BY cal.day_of_week;
