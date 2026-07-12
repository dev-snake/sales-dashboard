-- ID: A07
-- Title: Hierarchy Depth Levels
-- Skills: Recursive CTE depth
-- Tables: categories
-- Params: none
-- Level: advanced

WITH RECURSIVE cat_tree AS (
    SELECT id, name, parent_id, 0 AS depth
    FROM categories
    WHERE parent_id IS NULL AND deleted_at IS NULL
    UNION ALL
    SELECT c.id, c.name, c.parent_id, ct.depth + 1
    FROM categories c
    INNER JOIN cat_tree ct ON c.parent_id = ct.id
    WHERE c.deleted_at IS NULL
)
SELECT depth, COUNT(*) AS node_count
FROM cat_tree
GROUP BY depth
ORDER BY depth;
