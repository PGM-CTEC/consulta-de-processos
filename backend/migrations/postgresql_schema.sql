-- PostgreSQL DDL Migration — REM-054: Schema Translation (Phase 2)
-- Translated from SQLite schema for consulta_processual_pg database
-- Generated: 2026-02-28
-- Requirements: PostgreSQL 15+

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS pg_trgm;  -- Text similarity search
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";  -- UUID generation (future)

-- ============================================================
-- Table: processes
-- ============================================================
CREATE TABLE IF NOT EXISTS processes (
    id                SERIAL PRIMARY KEY,
    number            VARCHAR(50)  NOT NULL UNIQUE,
    class_nature      VARCHAR(255),
    subject           VARCHAR(255),
    court             VARCHAR(255),
    tribunal_name     VARCHAR(100),
    court_unit        VARCHAR(255),
    district          VARCHAR(255),
    judge             VARCHAR(255),
    distribution_date TIMESTAMPTZ,
    phase             VARCHAR(100),
    last_update       TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    raw_data          JSONB,
    deleted_at        TIMESTAMPTZ
);

-- Indexes for processes
CREATE INDEX IF NOT EXISTS ix_processes_number      ON processes (number);
CREATE INDEX IF NOT EXISTS ix_processes_deleted_at  ON processes (deleted_at);
CREATE INDEX IF NOT EXISTS ix_processes_tribunal    ON processes (tribunal_name);
CREATE INDEX IF NOT EXISTS ix_processes_district    ON processes (district);
-- GIN index for full-text search on subject/court
CREATE INDEX IF NOT EXISTS ix_processes_subject_trgm ON processes USING GIN (subject gin_trgm_ops);
-- GIN index for JSONB column (fast key/value queries inside raw_data) — REM-045
CREATE INDEX IF NOT EXISTS ix_processes_raw_data_gin ON processes USING GIN (raw_data);

-- ============================================================
-- Table: movements
-- ============================================================
CREATE TABLE IF NOT EXISTS movements (
    id          SERIAL PRIMARY KEY,
    process_id  INTEGER      NOT NULL REFERENCES processes (id) ON DELETE CASCADE,
    date        TIMESTAMPTZ  NOT NULL,
    description TEXT         NOT NULL,
    code        VARCHAR(50),
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    deleted_at  TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS ix_movements_process_id  ON movements (process_id);
CREATE INDEX IF NOT EXISTS ix_movements_deleted_at  ON movements (deleted_at);
CREATE INDEX IF NOT EXISTS ix_movements_date        ON movements (date DESC);

-- ============================================================
-- Table: search_history
-- ============================================================
CREATE TABLE IF NOT EXISTS search_history (
    id         SERIAL PRIMARY KEY,
    number     VARCHAR(50)  NOT NULL,
    court      VARCHAR(255),
    created_at TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_search_history_number     ON search_history (number);
CREATE INDEX IF NOT EXISTS ix_search_history_created_at ON search_history (created_at DESC);

-- ============================================================
-- Table: audit_log
-- ============================================================
CREATE TABLE IF NOT EXISTS audit_log (
    id          SERIAL PRIMARY KEY,
    table_name  VARCHAR(50)  NOT NULL,
    record_id   INTEGER,
    action      VARCHAR(10)  NOT NULL CHECK (action IN ('INSERT', 'UPDATE', 'DELETE')),
    old_values  TEXT,
    new_values  TEXT,
    user_id     VARCHAR(255),
    timestamp   TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_audit_log_table_name ON audit_log (table_name);
CREATE INDEX IF NOT EXISTS ix_audit_log_timestamp  ON audit_log (timestamp DESC);
CREATE INDEX IF NOT EXISTS ix_audit_log_record_id  ON audit_log (record_id);

-- ============================================================
-- Function: update_last_update
-- Automatically updates last_update on processes row change
-- ============================================================
CREATE OR REPLACE FUNCTION update_last_update()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_update = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_processes_last_update
    BEFORE UPDATE ON processes
    FOR EACH ROW
    EXECUTE FUNCTION update_last_update();

-- ============================================================
-- Migration validation query
-- Run after migration to verify schema integrity
-- ============================================================
-- SELECT table_name, column_name, data_type
-- FROM information_schema.columns
-- WHERE table_schema = 'public'
-- ORDER BY table_name, ordinal_position;
