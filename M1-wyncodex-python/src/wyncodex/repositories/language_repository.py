import sqlite3

from wyncodex.domain.language import Language


class LanguageRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def create(
            self,
            language: Language,
            *,
            commit: bool = True,
    ) -> Language:
        cursor = self._connection.execute(
            """
            INSERT INTO languages (
                uuid,
                name,
                slug,
                description,
                color,
                icon_name,
                is_enabled,
                sort_order
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                language.uuid,
                language.name,
                language.slug,
                language.description,
                language.color,
                language.icon_name,
                language.is_enabled,
                language.sort_order,
            ),
        )

        if commit:
            self._connection.commit()

        row = self._connection.execute(
            """
            SELECT *
            FROM languages
            WHERE id = ?
            """,
            (cursor.lastrowid,),
        ).fetchone()

        if row is None:
            raise RuntimeError("Created language could not be loaded.")

        return self._from_row(row)

    def get_by_id(self, language_id: int) -> Language | None:
        row = self._connection.execute(
            """
            SELECT *
            FROM languages
            WHERE id = ?
            """,
            (language_id,),
        ).fetchone()

        if row is None:
            return None

        return self._from_row(row)

    def get_all(self) -> list[Language]:
        rows = self._connection.execute(
            """
            SELECT *
            FROM languages
            ORDER BY sort_order, name
            """
        ).fetchall()

        return [
            self._from_row(row)
            for row in rows
        ]

    @staticmethod
    def _from_row(row: sqlite3.Row) -> Language:
        return Language(
            id=row["id"],
            uuid=row["uuid"],
            name=row["name"],
            slug=row["slug"],
            description=row["description"],
            color=row["color"],
            icon_name=row["icon_name"],
            is_enabled=bool(row["is_enabled"]),
            sort_order=row["sort_order"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def get_by_slug(self, slug: str) -> Language | None:
        row = self._connection.execute(
            """
            SELECT * FROM languages
                WHERE slug = ?
            """,
            (slug,),
        ).fetchone()

        if row is None:
            return None

        return self._from_row(row)