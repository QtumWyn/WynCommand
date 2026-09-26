import sqlite3

from wyncodex.domain.package import Package


class PackageRepository:
    def __init__(
            self,
            connection: sqlite3.Connection,
    ) -> None:
        self._connection = connection

    def create(
            self,
            package: Package,
            commit: bool = True,
    ) -> Package:
        cursor = self._connection.execute(
            """
            INSERT INTO packages (
                uuid,
                category_id,
                name,
                slug,
                summary,
                description,
                sort_order
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                package.uuid,
                package.category_id,
                package.name,
                package.slug,
                package.summary,
                package.description,
                package.sort_order,
            ),
        )

        if commit:
            self._connection.commit()

        row = self._connection.execute(
            """
            SELECT *
            FROM packages
            WHERE id = ?
            """,
            (cursor.lastrowid,),
        ).fetchone()

        if row is None:
            raise RuntimeError(
                "Created package could not be loaded."
            )

        return self._from_row(row)

    def get_by_id(
            self,
            package_id: int,
    ) -> Package | None:
        row = self._connection.execute(
            """
            SELECT *
            FROM packages
            WHERE id = ?
            """,
            (package_id,),
        ).fetchone()

        if row is None:
            return None

        return self._from_row(row)

    def get_by_slug(
            self,
            category_id: int,
            slug: str,
    ) -> Package | None:
        row = self._connection.execute(
            """
            SELECT *
            FROM packages
            WHERE category_id = ?
              AND slug = ?
            """,
            (
                category_id,
                slug,
            ),
        ).fetchone()

        if row is None:
            return None

        return self._from_row(row)

    def get_for_category(
            self,
            category_id: int,
    ) -> list[Package]:
        rows = self._connection.execute(
            """
            SELECT *
            FROM packages
            WHERE category_id = ?
            ORDER BY sort_order, name
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
    ) -> Package:
        return Package(
            id=row["id"],
            uuid=row["uuid"],
            category_id=row["category_id"],
            name=row["name"],
            slug=row["slug"],
            summary=row["summary"],
            description=row["description"],
            sort_order=row["sort_order"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )