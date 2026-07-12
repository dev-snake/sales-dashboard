-- ID: A35
-- Title: Deduplicate Keep Latest
-- Skills: ROW_NUMBER quality
-- Tables: customers
-- Params: none
-- Level: advanced

-- Pattern: keep latest row per natural key (demo on customers email when not null)
WITH ranked AS (
    SELECT
        c.*,
        ROW_NUMBER() OVER (
            PARTITION BY LOWER(c.email)
            ORDER BY c.updated_at DESC NULLS LAST, c.id DESC
        ) AS rn
    FROM customers c
    WHERE c.email IS NOT NULL
      AND c.deleted_at IS NULL
)
SELECT id, code, email, first_name, last_name, updated_at
FROM ranked
WHERE rn = 1
ORDER BY email
LIMIT 100;
