import sqlite3
from importlib.resources import files

MIGRATION_PACKAGE = "wyncodex.database.migrations"


def run_migrations(connection: sqlite3.Connection) -> None:
    _ensure_migration_table(connection)

    applied_versions = _load_applied_versions(connection)

    migration_files = sorted(
        resource
        for resource in files(MIGRATION_PACKAGE).iterdir()
        if resource.name.endswith(".sql")
    )

    for migration_file in migration_files:
        version = _parse_version(migration_file.name)

        if version in applied_versions:
            continue

        sql = migration_file.read_text(encoding="utf-8")

        migration_script = f"""
            BEGIN IMMEDIATE;
    
            {sql}
    
            INSERT INTO schema_migrations (version)
            VALUES ({version});
    
            COMMIT;
        """

        try:
            connection.executescript(migration_script)
        except sqlite3.Error:
            connection.rollback()
            raise

def _ensure_migration_table(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations
        (
            version    INTEGER PRIMARY KEY,
            applied_at TEXT NOT NULL
                DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
        )
        """
    )
    connection.commit()

def _load_applied_versions(connection: sqlite3.Connection) -> set[int]:
    rows = connection.execute(
        "SELECT version FROM schema_migrations"
    ).fetchall()

    return {row["version"] for row in rows}

def _parse_version(filename: str) -> int:
    prefix, separator, _ = filename.partition("_")

    if not separator or not prefix.isdigit():
        raise ValueError(
            f"Invalid migration filename: {filename!r}"
        )
    return int(prefix)

