import sqlite3

from wyncodex.domain.argument import Argument


class ArgumentRepository:
    def __init__(
            self,
            connection: sqlite3.Connection,
    ) -> None:
        self._connection = connection

    def create(
            self,
            argument: Argument,
            *,
            commit: bool = True,
    ) -> Argument:
        cursor = self._connection.execute(
            """
            INSERT INTO arguments (
                uuid,
                entry_id,
                position,
                name,
                type_text,
                description,
                required,
                default_value
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                argument.uuid,
                argument.entry_id,
                argument.position,
                argument.name,
                argument.type_text,
                argument.description,
                int(argument.required),
                argument.default_value,
            ),
        )

        if commit:
            self._connection.commit()

        row = self._connection.execute(
            """
            SELECT *
            FROM arguments
            WHERE id = ?
            """,
            (cursor.lastrowid,),
        ).fetchone()

        if row is None:
            raise RuntimeError(
                "Created argument could not be loaded."
            )

        return self._from_row(row)

    def get_for_entry(
            self,
            entry_id: int,
    ) -> list[Argument]:
        rows = self._connection.execute(
            """
            SELECT *
            FROM arguments
            WHERE entry_id = ?
            ORDER BY position, id
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
    ) -> Argument:
        return Argument(
            id=row["id"],
            uuid=row["uuid"],
            entry_id=row["entry_id"],
            position=row["position"],
            name=row["name"],
            type_text=row["type_text"],
            description=row["description"],
            required=bool(row["required"]),
            default_value=row["default_value"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def delete_for_entry(
            self,
            entry_id: int,
            *,
            commit: bool = True,
    ) -> None:
        self._connection.execute(
            """
            DELETE FROM arguments
            WHERE entry_id = ?
            """,
            (entry_id,),
        )

        if commit:
            self._connection.commit()