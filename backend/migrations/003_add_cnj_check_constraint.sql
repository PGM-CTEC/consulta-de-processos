-- Migration 003: Add CNJ Number CHECK Constraint
-- Story: REM-009 (DB-007)
-- Description: Validate CNJ number format (20 numeric digits only)
-- Date: 2026-02-22

-- SQLite requires table recreation to add constraints
-- Step 1: Create new table with CHECK constraint
CREATE TABLE processes_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    number VARCHAR UNIQUE NOT NULL CHECK (LENGTH(number) = 20 AND TYPEOF(number) = 'text'),
    class_nature VARCHAR,
    subject VARCHAR,
    court VARCHAR,
    tribunal_name VARCHAR,
    court_unit VARCHAR,
    district VARCHAR,
    distribution_date DATETIME,
    phase VARCHAR CHECK (phase IS NULL OR (phase >= '01' AND phase <= '15')),
    last_update DATETIME,
    raw_data JSON
);

-- Step 2: Copy data from old table
INSERT INTO processes_new (id, number, class_nature, subject, court, tribunal_name, court_unit, district, distribution_date, phase, last_update, raw_data)
SELECT id, number, class_nature, subject, court, tribunal_name, court_unit, district, distribution_date, phase, last_update, raw_data FROM processes;

-- Step 3: Drop old table
DROP TABLE processes;

-- Step 4: Rename new table to original name
ALTER TABLE processes_new RENAME TO processes;

-- Step 5: Recreate indexes
CREATE UNIQUE INDEX idx_process_number ON processes(number);

-- Verification
SELECT COUNT(*) as total_processes FROM processes;
