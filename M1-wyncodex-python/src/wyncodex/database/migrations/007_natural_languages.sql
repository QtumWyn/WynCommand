ALTER TABLE languages ADD COLUMN language_kind TEXT NOT NULL DEFAULT 'programming'
    CHECK (language_kind IN ('programming', 'natural'));
ALTER TABLE entries ADD COLUMN formality TEXT;
ALTER TABLE entries ADD COLUMN dialect TEXT;
ALTER TABLE entries ADD COLUMN related_concepts TEXT;
ALTER TABLE examples ADD COLUMN romanization TEXT;
ALTER TABLE examples ADD COLUMN pronunciation TEXT;
CREATE INDEX idx_languages_kind ON languages(language_kind, sort_order, name);
