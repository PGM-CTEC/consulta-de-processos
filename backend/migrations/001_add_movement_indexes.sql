-- Migration 001: Add Missing Movement Indexes
-- Story: REM-001 (DB-001)
-- Impact: 20-100x query speedup for movement searches
-- Date: 2026-02-22

-- Index 1: Composite index for process_id + date (most common query pattern)
-- Used in: "SELECT * FROM movements WHERE process_id = ? ORDER BY date DESC"
CREATE INDEX IF NOT EXISTS idx_movement_process_date
ON movements(process_id, date DESC);

-- Index 2: Code lookup index (used in movement filtering)
-- Used in: "SELECT * FROM movements WHERE code = ?"
CREATE INDEX IF NOT EXISTS idx_movement_code
ON movements(code);

-- Index 3: Date-only index (used in chronological queries)
-- Used in: "SELECT * FROM movements ORDER BY date DESC"
CREATE INDEX IF NOT EXISTS idx_movement_date
ON movements(date DESC);

-- Verification: Check index creation
SELECT
    name,
    tbl_name,
    sql
FROM sqlite_master
WHERE type = 'index'
    AND tbl_name = 'movements'
    AND name LIKE 'idx_movement_%'
ORDER BY name;
