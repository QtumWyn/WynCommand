import sqlite3

from wyncodex.domain.category import Category


class CategoryRepository:
    def __init__(
            self,
            connection: sqlite3.Connection,
    ) -> None:
        self._connection = connection

    def create(
            self,
            category: Category,
            commit: bool = True,
    ) -> Category:
        cursor = self._connection.execute(
            """
            INSERT INTO categories (
                uuid,
                language_id,
                name,
                slug,
                description,
                sort_order
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                category.uuid,
                category.language_id,
                category.name,
                category.slug,
                category.description,
                category.sort_order,
            ),
        )

        if commit:
            self._connection.commit()

        row = self._connection.execute(
            """
            SELECT *
            FROM categories
            WHERE id = ?
            """,
            (cursor.lastrowid,),
        ).fetchone()

        if row is None:
            raise RuntimeError(
                "Created category could not be loaded."
            )

        return self._from_row(row)

    def get_by_id(
            self,
            category_id: int,
    ) -> Category | None:
        row = self._connection.execute(
            """
            SELECT *
            FROM categories
            WHERE id = ?
            """,
            (category_id,),
        ).fetchone()

        if row is None:
            return None

        return self._from_row(row)

    def get_by_slug(
            self,
            language_id: int,
            slug: str,
    ) -> Category | None:
        row = self._connection.execute(
            """
            SELECT *
            FROM categories
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

    def get_for_language(
            self,
            language_id: int,
    ) -> list[Category]:
        rows = self._connection.execute(
            """
            SELECT *
            FROM categories
            WHERE language_id = ?
            ORDER BY sort_order, name
            """,
            (language_id,),
        ).fetchall()

        return [
            self._from_row(row)
            for row in rows
        ]

    @staticmethod
    def _from_row(
            row: sqlite3.Row,
    ) -> Category:
        return Category(
            id=row["id"],
            uuid=row["uuid"],
            language_id=row["language_id"],
            name=row["name"],
            slug=row["slug"],
            description=row["description"],
            sort_order=row["sort_order"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )