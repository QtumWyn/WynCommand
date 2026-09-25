import sqlite3

from wyncodex.domain.example import Example


class ExampleRepository:
    def __init__(
            self,
            connection: sqlite3.Connection,
    ) -> None:
        self._connection = connection

    def create(
            self,
            example: Example,
    ) -> Example:
        cursor = self._connection.execute(
            """
            INSERT INTO examples (
                uuid,
                entry_id,
                title,
                code,
                explanation,
                example_type,
                syntax_hint,
                sort_order
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                example.uuid,
                example.entry_id,
                example.title,
                example.code,
                example.explanation,
                example.example_type,
                example.syntax_hint,
                example.sort_order,
            ),
        )

        self._connection.commit()

        row = self._connection.execute(
            """
            SELECT *
            FROM examples
            WHERE id = ?
            """,
            (cursor.lastrowid,),
        ).fetchone()

        if row is None:
            raise RuntimeError(
                "Created example could not be loaded."
            )

        return self._from_row(row)

    def get_for_entry(
            self,
            entry_id: int,
    ) -> list[Example]:
        rows = self._connection.execute(
            """
            SELECT *
            FROM examples
            WHERE entry_id = ?
            ORDER BY sort_order, id
            """,
            (entry_id,),
        ).fetchall()

        return [
            self._from_row(row)
            for row in rows
        ]

    @staticmethod
    def _from_row(
            row: sqlite3.Row,
    ) -> Example:
        return Example(
            id=row["id"],
            uuid=row["uuid"],
            entry_id=row["entry_id"],
            title=row["title"],
            code=row["code"],
            explanation=row["explanation"],
            example_type=row["example_type"],
            syntax_hint=row["syntax_hint"],
            sort_order=row["sort_order"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def delete_for_entry(
            self,
            entry_id: int,
    ) -> None:
        self._connection.execute(
            """
            DELETE FROM examples
            WHERE entry_id = ?
            """,
            (entry_id,),
        )

        self._connection.commit()