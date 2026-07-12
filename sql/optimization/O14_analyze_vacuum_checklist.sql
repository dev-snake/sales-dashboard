-- ID: O14
-- Title: Analyze Vacuum Checklist
-- Skills: ops
-- Tables: —
-- Params: none
-- Level: optimization

-- Operational checklist (run manually in psql, not a result-set query)
-- 1) ANALYZE orders;
-- 2) ANALYZE order_items;
-- 3) VACUUM (VERBOSE, ANALYZE) orders;
-- 4) Check bloat / dead tuples:
SELECT
    relname AS table_name,
    n_live_tup,
    n_dead_tup,
    last_analyze,
    last_autoanalyze
FROM pg_stat_user_tables
WHERE schemaname = 'public'
ORDER BY n_dead_tup DESC;
