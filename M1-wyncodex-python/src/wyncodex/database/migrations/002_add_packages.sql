CREATE TABLE packages (
                          id INTEGER PRIMARY KEY,
                          uuid TEXT NOT NULL UNIQUE,

                          category_id INTEGER NOT NULL,

                          name TEXT NOT NULL,
                          slug TEXT NOT NULL,

                          summary TEXT,
                          description TEXT,

                          sort_order INTEGER NOT NULL DEFAULT 0,

                          created_at TEXT NOT NULL
                                                      DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),

                          updated_at TEXT NOT NULL
                                                      DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),

                          UNIQUE (category_id, slug),

                          FOREIGN KEY (category_id)
                              REFERENCES categories(id)
                              ON DELETE CASCADE
);


ALTER TABLE entries
    ADD COLUMN package_id INTEGER
        REFERENCES packages(id)
            ON DELETE SET NULL;


CREATE INDEX idx_packages_category_sort
    ON packages(category_id, sort_order);


CREATE INDEX idx_entries_package_sort
    ON entries(package_id, sort_order);