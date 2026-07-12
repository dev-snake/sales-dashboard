-- ID: A04
-- Title: Category Tree Recursive
-- Skills: Recursive CTE
-- Tables: categories
-- Params: none
-- Level: advanced

WITH RECURSIVE cat_tree AS (
    SELECT id, code, name, parent_id, 1 AS depth, name::text AS path
    FROM categories
    WHERE parent_id IS NULL
      AND deleted_at IS NULL
    UNION ALL
    SELECT c.id, c.code, c.name, c.parent_id, ct.depth + 1,
           ct.path || ' > ' || c.name
    FROM categories c
    INNER JOIN cat_tree ct ON c.parent_id = ct.id
    WHERE c.deleted_at IS NULL
)
SELECT id, code, name, parent_id, depth, path
FROM cat_tree
ORDER BY path;
