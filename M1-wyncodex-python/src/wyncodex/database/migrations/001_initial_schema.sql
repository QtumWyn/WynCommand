CREATE TABLE languages (
                           id INTEGER PRIMARY KEY,
                           uuid TEXT NOT NULL UNIQUE,

                           name TEXT NOT NULL,
                           slug TEXT NOT NULL UNIQUE,
                           description TEXT,

                           color TEXT,
                           icon_name TEXT,

                           is_enabled INTEGER NOT NULL DEFAULT 1
                               CHECK (is_enabled IN (0, 1)),

                           sort_order INTEGER NOT NULL DEFAULT 0,

                           created_at TEXT NOT NULL
                                                       DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),

                           updated_at TEXT NOT NULL
                                                       DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);


CREATE TABLE categories (
                            id INTEGER PRIMARY KEY,
                            uuid TEXT NOT NULL UNIQUE,

                            language_id INTEGER NOT NULL,

                            name TEXT NOT NULL,
                            slug TEXT NOT NULL,
                            description TEXT,

                            sort_order INTEGER NOT NULL DEFAULT 0,

                            created_at TEXT NOT NULL
                                                        DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),

                            updated_at TEXT NOT NULL
                                                        DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),

                            UNIQUE (language_id, slug),

                            FOREIGN KEY (language_id)
                                REFERENCES languages(id)
                                ON DELETE CASCADE
);


CREATE TABLE entries (
                         id INTEGER PRIMARY KEY,
                         uuid TEXT NOT NULL UNIQUE,

                         language_id INTEGER NOT NULL,
                         category_id INTEGER,

                         title TEXT NOT NULL,
                         slug TEXT NOT NULL,

                         signature TEXT,
                         definition TEXT,
                         mental_model TEXT,
                         return_value TEXT,
                         gotchas TEXT,
                         notes TEXT,

                         sort_order INTEGER NOT NULL DEFAULT 0,

                         created_at TEXT NOT NULL
                                                     DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),

                         updated_at TEXT NOT NULL
                                                     DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),

                         UNIQUE (language_id, slug),

                         FOREIGN KEY (language_id)
                             REFERENCES languages(id)
                             ON DELETE CASCADE,

                         FOREIGN KEY (category_id)
                             REFERENCES categories(id)
                             ON DELETE SET NULL
);


CREATE TABLE arguments (
                           id INTEGER PRIMARY KEY,
                           uuid TEXT NOT NULL UNIQUE,

                           entry_id INTEGER NOT NULL,

                           position INTEGER NOT NULL DEFAULT 0,

                           name TEXT NOT NULL,
                           type_text TEXT,
                           description TEXT,

                           required INTEGER NOT NULL DEFAULT 1
                               CHECK (required IN (0, 1)),

                           default_value TEXT,

                           created_at TEXT NOT NULL
                                                     DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),

                           updated_at TEXT NOT NULL
                                                     DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),

                           FOREIGN KEY (entry_id)
                               REFERENCES entries(id)
                               ON DELETE CASCADE
);


CREATE TABLE examples (
                          id INTEGER PRIMARY KEY,
                          uuid TEXT NOT NULL UNIQUE,

                          entry_id INTEGER NOT NULL,

                          title TEXT,
                          code TEXT NOT NULL,
                          explanation TEXT,

                          example_type TEXT NOT NULL DEFAULT 'practical',
                          syntax_hint TEXT,

                          sort_order INTEGER NOT NULL DEFAULT 0,

                          created_at TEXT NOT NULL
                              DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),

                          updated_at TEXT NOT NULL
                              DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),

                          FOREIGN KEY (entry_id)
                              REFERENCES entries(id)
                              ON DELETE CASCADE
);


CREATE TABLE tags (
                      id INTEGER PRIMARY KEY,
                      uuid TEXT NOT NULL UNIQUE,

                      name TEXT NOT NULL,
                      slug TEXT NOT NULL UNIQUE,

                      created_at TEXT NOT NULL
                          DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),

                      updated_at TEXT NOT NULL
                          DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);


CREATE TABLE entry_tags (
                            entry_id INTEGER NOT NULL,
                            tag_id INTEGER NOT NULL,

                            PRIMARY KEY (entry_id, tag_id),

                            FOREIGN KEY (entry_id)
                                REFERENCES entries(id)
                                ON DELETE CASCADE,

                            FOREIGN KEY (tag_id)
                                REFERENCES tags(id)
                                ON DELETE CASCADE
);


CREATE TABLE entry_relations (
                                 id INTEGER PRIMARY KEY,
                                 uuid TEXT NOT NULL UNIQUE,

                                 source_entry_id INTEGER NOT NULL,
                                 target_entry_id INTEGER NOT NULL,

                                 relation_type TEXT NOT NULL DEFAULT 'related',
                                 sort_order INTEGER NOT NULL DEFAULT 0,

                                 created_at TEXT NOT NULL
                                                             DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),

                                 updated_at TEXT NOT NULL
                                                             DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),

                                 CHECK (source_entry_id != target_entry_id),

                                 UNIQUE (
                                         source_entry_id,
                                         target_entry_id,
                                         relation_type
                                     ),

                                 FOREIGN KEY (source_entry_id)
                                     REFERENCES entries(id)
                                     ON DELETE CASCADE,

                                 FOREIGN KEY (target_entry_id)
                                     REFERENCES entries(id)
                                     ON DELETE CASCADE
);


CREATE INDEX idx_categories_language_sort
    ON categories(language_id, sort_order);


CREATE INDEX idx_entries_language_category
    ON entries(language_id, category_id);


CREATE INDEX idx_entries_category_sort
    ON entries(category_id, sort_order);


CREATE INDEX idx_arguments_entry_position
    ON arguments(entry_id, position);


CREATE INDEX idx_examples_entry_sort
    ON examples(entry_id, sort_order);


CREATE INDEX idx_entry_tags_tag
    ON entry_tags(tag_id);


CREATE INDEX idx_entry_relations_source
    ON entry_relations(source_entry_id);


CREATE INDEX idx_entry_relations_target
    ON entry_relations(target_entry_id);