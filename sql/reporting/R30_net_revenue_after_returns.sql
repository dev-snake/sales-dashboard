-- ID: R30
-- Title: Net Revenue After Returns
-- Skills: net revenue
-- Tables: orders, order_items, returns
-- Params: :start_date, :end_date optional (see comments)
-- Level: reporting

WITH gross AS (
    SELECT SUM(oi.line_total) AS gross_revenue
    FROM order_items oi
    INNER JOIN orders o ON o.id = oi.order_id
    WHERE o.status IN ('paid', 'completed')
),
refunds AS (
    SELECT COALESCE(SUM(refund_amount), 0) AS total_refunds
    FROM returns
    WHERE status IN ('approved', 'completed')
)
SELECT
    g.gross_revenue,
    r.total_refunds,
    g.gross_revenue - r.total_refunds AS net_revenue
FROM gross g
CROSS JOIN refunds r;
