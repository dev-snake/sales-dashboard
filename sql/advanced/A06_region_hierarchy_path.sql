-- ID: A06
-- Title: Region Hierarchy Path
-- Skills: Recursive CTE
-- Tables: regions
-- Params: none
-- Level: advanced

WITH RECURSIVE region_tree AS (
    SELECT id, code, name, parent_id, level, name::text AS path
    FROM regions
    WHERE parent_id IS NULL
      AND deleted_at IS NULL
    UNION ALL
    SELECT r.id, r.code, r.name, r.parent_id, r.level,
           rt.path || ' / ' || r.name
    FROM regions r
    INNER JOIN region_tree rt ON r.parent_id = rt.id
    WHERE r.deleted_at IS NULL
)
SELECT id, code, name, parent_id, level, path
FROM region_tree
ORDER BY path;
