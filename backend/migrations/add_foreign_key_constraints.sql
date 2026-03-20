-- Migration: Add foreign key constraints to search_history
-- REM-044: Referential integrity for search_history → processes

-- For SQLite (current DB)
-- SQLite requires recreating the table to add FK constraints

CREATE TABLE IF NOT EXISTS search_history_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    process_id INTEGER NOT NULL,
    searched_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    search_term VARCHAR(255),
    FOREIGN KEY (process_id) REFERENCES processes(id) ON DELETE CASCADE
);

-- Copy existing data
INSERT INTO search_history_new SELECT * FROM search_history;
DROP TABLE search_history;
ALTER TABLE search_history_new RENAME TO search_history;

-- For PostgreSQL (future migration)
-- ALTER TABLE search_history ADD CONSTRAINT fk_search_history_process_id
--     FOREIGN KEY (process_id) REFERENCES processes(id) ON DELETE CASCADE;
