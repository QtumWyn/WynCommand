ALTER TABLE entries
    ADD COLUMN parent_entry_id INTEGER
        REFERENCES entries(id)
            ON DELETE CASCADE;

ALTER TABLE entries
    ADD COLUMN entry_kind TEXT NOT NULL
        DEFAULT 'entry';

CREATE INDEX IF NOT EXISTS idx_entries_parent_entry_id
    ON entries(parent_entry_id);