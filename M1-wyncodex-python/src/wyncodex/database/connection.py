import sqlite3
from pathlib import Path

def open_database(database_file: Path) -> sqlite3.Connection:
    database_file.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(database_file)

    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    foreign_keys_enabled = connection.execute(
        "PRAGMA foreign_keys"
    ).fetchone()[0]

    if foreign_keys_enabled != 1:
        connection.closed()
        raise RuntimeError("SQLite foreign-key enforcement could not be enabled.")
    return connection