import sqlite3

from wyncodex.domain.entry import Entry


class EntryRepository:
    def __init__(
            self,
            connection: sqlite3.Connection,
    ) -> None:
        self._connection = connection

    def create(
            self,
            entry: Entry,
            *,
            commit: bool = True,
    ) -> Entry:
        cursor = self._connection.execute(
            """
            INSERT INTO entries (
                uuid,
                language_id,
                category_id,
                package_id,
                title,
                slug,
                summary,
                signature,
                definition,
                mental_model,
                return_value,
                gotchas,
                notes,
                sort_order
            )
            VALUES (
                       ?, ?, ?, ?, ?, ?, ?,
                       ?, ?, ?, ?, ?, ?, ?
                   )
            """,
            (
                entry.uuid,
                entry.language_id,
                entry.category_id,
                entry.package_id,
                entry.title,
                entry.slug,
                entry.summary,
                entry.signature,
                entry.definition,
                entry.mental_model,
                entry.return_value,
                entry.gotchas,
                entry.notes,
                entry.sort_order,
            ),
        )

        if commit:
            self._connection.commit()

        row = self._connection.execute(
            """
            SELECT *
            FROM entries
            WHERE id = ?
            """,
            (cursor.lastrowid,),
        ).fetchone()

        if row is None:
            raise RuntimeError(
                "Created entry could not be loaded."
            )

        return self._from_row(row)

    def get_by_id(
            self,
            entry_id: int,
    ) -> Entry | None:
        row = self._connection.execute(
            """
            SELECT *
            FROM entries
            WHERE id = ?
            """,
            (entry_id,),
        ).fetchone()

        if row is None:
            return None

        return self._from_row(row)

    def get_by_slug(
            self,
            language_id: int,
            slug: str,
    ) -> Entry | None:
        row = self._connection.execute(
            """
            SELECT *
            FROM entries
            WHERE language_id = ?
              AND slug = ?
            """,
            (
                language_id,
                slug,
            ),
        ).fetchone()

        if row is None:
            return None

        return self._from_row(row)

    def get_for_package(
            self,
            package_id: int,
    ) -> list[Entry]:
        rows = self._connection.execute(
            """
            SELECT *
            FROM entries
            WHERE package_id = ?
            ORDER BY sort_order, title
            """,
            (package_id,),
        ).fetchall()

        return [
            self._from_row(row)
            for row in rows
        ]

    def get_direct_for_category(
            self,
            category_id: int,
    ) -> list[Entry]:
        rows = self._connection.execute(
            """
            SELECT *
            FROM entries
            WHERE category_id = ?
              AND package_id IS NULL
            ORDER BY sort_order, title
            """,
            (category_id,),
        ).fetchall()

        return [
            self._from_row(row)
            for row in rows
        ]

    @staticmethod
    def _from_row(
            row: sqlite3.Row,
    ) -> Entry:
        return Entry(
            id=row["id"],
            uuid=row["uuid"],
            language_id=row["language_id"],
            category_id=row["category_id"],
            package_id=row["package_id"],
            title=row["title"],
            slug=row["slug"],
            summary=row["summary"],
            signature=row["signature"],
            definition=row["definition"],
            mental_model=row["mental_model"],
            return_value=row["return_value"],
            gotchas=row["gotchas"],
            notes=row["notes"],
            sort_order=row["sort_order"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def delete(
            self,
            entry_id: int,
            *,
            commit: bool = True,
    ) -> None:
        self._connection.execute(
            """
            DELETE FROM entries
            WHERE id = ?
            """,
            (entry_id,),
        )

        if commit:
            self._connection.commit()

    def update(
            self,
            entry: Entry,
            *,
            commit: bool = True,
    ) -> Entry:
        if entry.id is None:
            raise ValueError(
                "Cannot update an unsaved entry."
            )

        self._connection.execute(
            """
            UPDATE entries
            SET
                title = ?,
                slug = ?,
                summary = ?,
                signature = ?,
                definition = ?,
                mental_model = ?,
                return_value = ?,
                gotchas = ?,
                notes = ?,
                updated_at = (
                    strftime(
                            '%Y-%m-%dT%H:%M:%fZ',
                            'now'
                    )
                    )
            WHERE id = ?
            """,
            (
                entry.title,
                entry.slug,
                entry.summary,
                entry.signature,
                entry.definition,
                entry.mental_model,
                entry.return_value,
                entry.gotchas,
                entry.notes,
                entry.id,
            ),
        )

        if commit:
            self._connection.commit()

        updated = self.get_by_id(
            entry.id
        )

        if updated is None:
            raise RuntimeError(
                "Updated entry could not be loaded."
            )

        return updated