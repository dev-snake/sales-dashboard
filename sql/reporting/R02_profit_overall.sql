-- ID: R02
-- Title: Profit Overall
-- Skills: aggregate
-- Tables: orders, order_items
-- Params: :start_date, :end_date optional (see comments)
-- Level: reporting

SELECT
    SUM(oi.line_total) AS revenue,
    SUM(oi.quantity * oi.unit_cost) AS cogs,
    SUM(oi.line_total) - SUM(oi.quantity * oi.unit_cost) AS gross_profit,
    ROUND(
        100.0 * (SUM(oi.line_total) - SUM(oi.quantity * oi.unit_cost))
        / NULLIF(SUM(oi.line_total), 0),
        2
    ) AS gross_margin_pct
FROM order_items oi
INNER JOIN orders o ON o.id = oi.order_id
WHERE o.status IN ('paid', 'completed')
  AND o.order_date >= CURRENT_DATE - INTERVAL '30 days';
