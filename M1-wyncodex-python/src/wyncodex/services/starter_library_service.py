import sqlite3

from importlib import resources

from wyncodex.importers.json_importer import (
    JsonImportService,
)

from wyncodex.importers.models import (
    ImportMode,
    ImportResult,
)


SEED_MARKER_KEY = (
    "starter_library_seed"
)

SEED_VERSION = (
    "v3-release"
)

RESOURCE_PACKAGE = (
    "wyncodex.resources"
)

RESOURCE_FILENAME = (
    "starter-library.json"
)


class StarterLibraryService:
    def __init__(
            self,
            connection: sqlite3.Connection,
            import_service: JsonImportService,
    ) -> None:
        self._connection = connection

        self._import_service = (
            import_service
        )

    def seed_if_needed(
            self,
    ) -> ImportResult | None:
        marker = (
            self._connection.execute(
                """
                SELECT value
                FROM app_metadata
                WHERE key = ?
                """,
                (
                    SEED_MARKER_KEY,
                ),
            )
            .fetchone()
        )

        if marker is not None:
            return None

        language_count_row = (
            self._connection.execute(
                """
                SELECT COUNT(*)
                FROM languages
                """
            )
            .fetchone()
        )

        language_count = (
            language_count_row[0]
            if language_count_row
               is not None
            else 0
        )

        # Existing WynCodex installation.
        #
        # Do NOT inject the starter library.
        # Just mark this DB as already
        # initialized.
        if language_count > 0:
            self._set_seed_marker(
                "existing-library"
            )

            return None

        resource = (
            resources.files(
                RESOURCE_PACKAGE
            )
            .joinpath(
                RESOURCE_FILENAME
            )
        )

        if not resource.is_file():
            raise RuntimeError(
                "Bundled WynCodex starter "
                "library could not be found."
            )

        with resources.as_file(
                resource
        ) as source_path:
            preview = (
                self._import_service.preview(
                    source_path,
                    mode=(
                        ImportMode
                        .STRICT_CREATE
                    ),
                )
            )

            result = (
                self._import_service
                .import_preview(
                    preview,
                    mode=(
                        ImportMode
                        .STRICT_CREATE
                    ),
                )
            )

        self._set_seed_marker(
            SEED_VERSION
        )

        return result

    def _set_seed_marker(
            self,
            value: str,
    ) -> None:
        self._connection.execute(
            """
            INSERT INTO app_metadata (
                key,
                value
            )
            VALUES (?, ?)

            ON CONFLICT(key)
                DO UPDATE SET
                              value = excluded.value,
                              updated_at = CURRENT_TIMESTAMP
            """,
            (
                SEED_MARKER_KEY,
                value,
            ),
        )

        self._connection.commit()