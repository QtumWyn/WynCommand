import sqlite3

from wyncodex.domain.search_result import (
    SearchResult,
)


class SearchRepository:
    def __init__(
            self,
            connection: sqlite3.Connection,
    ) -> None:
        self._connection = connection

    def search(
            self,
            query: str,
            *,
            language_id: int | None = None,
            limit: int = 50,
            assembly_track: int | None = None,
            language_kind: str | None = None,
    ) -> list[SearchResult]:
        normalized_query = (
            " ".join(
                query.casefold().split()
            )
        )

        if not normalized_query:
            return []

        terms = normalized_query.split()

        rows = self._connection.execute(
            """
            WITH RECURSIVE entry_paths (
                                        id,
                                        path
                ) AS (
                SELECT
                    id,
                    title
                FROM entries
                WHERE parent_entry_id IS NULL

                UNION ALL

                SELECT
                    child.id,
                    entry_paths.path
                        || ' › '
                        || child.title
                FROM entries AS child
                         JOIN entry_paths
                              ON child.parent_entry_id
                                  = entry_paths.id
            )

            SELECT
                e.id AS entry_id,
                e.title,
                e.entry_kind,

                e.summary,
                e.signature,
                e.definition,
                e.mental_model,
                e.return_value,
                e.gotchas,
                e.notes, e.formality, e.dialect, e.related_concepts,

                l.name AS language_name,
                l.slug AS language_slug,
                c.name AS category_name,
                p.name AS package_name,

                COALESCE(
                        entry_paths.path,
                        e.title
                ) AS entry_path,

                COALESCE(
                        (
                            SELECT group_concat(
                                           COALESCE(a.name, '')
                                               || ' '
                                               || COALESCE(
                                                   a.type_text,
                                                   ''
                                                  )
                                               || ' '
                                               || COALESCE(
                                                   a.description,
                                                   ''
                                                  )
                                               || ' '
                                               || COALESCE(
                                                   a.default_value,
                                                   ''
                                                  ),
                                           ' '
                                   )
                            FROM arguments AS a
                            WHERE a.entry_id = e.id
                        ),
                        ''
                ) AS argument_text,

                COALESCE(
                        (
                            SELECT group_concat(
                                           COALESCE(x.title, '')
                                               || ' '
                                               || COALESCE(x.code, '') || ' ' || COALESCE(x.romanization, '') || ' ' || COALESCE(x.pronunciation, '')
                                               || ' '
                                               || COALESCE(
                                                   x.output,
                                                   ''
                                                  )
                                               || ' '
                                               || COALESCE(
                                                   x.explanation,
                                                   ''
                                                  )
                                               || ' '
                                               || COALESCE(
                                                   x.example_type,
                                                   ''
                                                  )
                                               || ' '
                                               || COALESCE(
                                                   x.syntax_hint,
                                                   ''
                                                  ),
                                           ' '
                                   )
                            FROM examples AS x
                            WHERE x.entry_id = e.id
                        ),
                        ''
                ) AS example_text

            FROM entries AS e

                     JOIN languages AS l
                          ON l.id = e.language_id

                     JOIN categories AS c
                          ON c.id = e.category_id

                     LEFT JOIN packages AS p
                               ON p.id = e.package_id

                     LEFT JOIN entry_paths
                               ON entry_paths.id = e.id

            WHERE (:language_id IS NULL
                   OR e.language_id = :language_id)
              AND (:language_kind IS NULL OR l.language_kind=:language_kind)
            """,
            {"language_id": language_id, "language_kind": language_kind},
        ).fetchall()

        results: list[SearchResult] = []

        allowed = None
        if assembly_track is not None:
            from wyncodex.services.assembly_service import AssemblyService
            allowed = AssemblyService(self._connection).entry_ids(assembly_track)

        for row in rows:
            if allowed is not None and row["entry_id"] not in allowed:
                continue
            result = self._match_row(
                row,
                normalized_query,
                terms,
            )

            if result is not None:
                results.append(result)

        results.sort(
            key=lambda result: (
                -result.score,
                result.language_name.casefold(),
                result.title.casefold(),
            )
        )

        return results[:limit]

    def _match_row(
            self,
            row: sqlite3.Row,
            query: str,
            terms: list[str],
    ) -> SearchResult | None:
        title = row["title"] or ""
        entry_kind = row["entry_kind"] or ""

        language = (
                row["language_name"] or ""
        )

        category = (
                row["category_name"] or ""
        )

        package = row["package_name"]

        entry_path = (
                row["entry_path"] or title
        )

        summary = row["summary"]

        fields: dict[str, str] = {
            "title": title,
            "kind": entry_kind,
            "language": language + " " + row["language_slug"] + (" assembly" if row["language_slug"] == "nasm" else " Belarusian" if row["language_slug"] == "natural-belorussian" else ""),
            "category": category,
            "package": package or "",
            "path": entry_path,
            "summary": summary or "",
            "signature": row["signature"] or "",
            "definition": row["definition"] or "",
            "mental_model": (
                    row["mental_model"] or ""
            ),
            "return_value": (
                    row["return_value"] or ""
            ),
            "gotchas": row["gotchas"] or "",
            "notes": " ".join(row[k] or "" for k in ("notes","formality","dialect","related_concepts")),
            "arguments": (
                    row["argument_text"] or ""
            ),
            "examples": (
                    row["example_text"] or ""
            ),
        }

        lowered = {
            name: value.casefold()
            for name, value in fields.items()
        }

        searchable_text = " ".join(
            lowered.values()
        )

        if not all(
                term in searchable_text
                for term in terms
        ):
            return None

        score = self._score(
            query,
            terms,
            lowered,
        )

        full_path_parts = [
            language,
            category,
        ]

        if package:
            full_path_parts.append(
                package
            )

        full_path_parts.extend(
            entry_path.split(" › ")
        )

        full_path = " › ".join(
            full_path_parts
        )

        preview = self._preview(
            query,
            terms,
            fields,
        )

        return SearchResult(
            entry_id=row["entry_id"],
            title=title,
            entry_kind=entry_kind,
            language_name=language,
            category_name=category,
            package_name=package,
            entry_path=entry_path,
            full_path=full_path,
            summary=summary,
            preview=preview,
            score=score,
        )

    @staticmethod
    def _score(
            query: str,
            terms: list[str],
            fields: dict[str, str],
    ) -> int:
        score = 0

        title = fields["title"]
        path = fields["path"]

        if title == query:
            score += 500

        elif title.startswith(query):
            score += 350

        elif query in title:
            score += 250

        if fields["language"] == query:
            score += 180

        if fields["category"] == query:
            score += 140

        if fields["package"] == query:
            score += 140

        if query in path:
            score += 100

        if query in fields["signature"]:
            score += 90

        if query in fields["summary"]:
            score += 80

        for term in terms:
            if term in title:
                score += 40

            if term in path:
                score += 25

            if term in fields["summary"]:
                score += 20

            if term in fields["signature"]:
                score += 20

            if term in fields["definition"]:
                score += 12

            if term in fields["mental_model"]:
                score += 10

            if term in fields["return_value"]:
                score += 10

            if term in fields["gotchas"]:
                score += 10

            if term in fields["arguments"]:
                score += 8

            if term in fields["examples"]:
                score += 6

        return score

    @staticmethod
    def _preview(
            query: str,
            terms: list[str],
            fields: dict[str, str],
    ) -> str:
        candidates = (
            fields["summary"],
            fields["definition"],
            fields["mental_model"],
            fields["signature"],
            fields["gotchas"],
            fields["notes"],
            fields["arguments"],
            fields["examples"],
        )

        for candidate in candidates:
            if not candidate:
                continue

            lowered = candidate.casefold()

            if (
                    query in lowered
                    or any(
                term in lowered
                for term in terms
            )
            ):
                return (
                    SearchRepository
                    ._trim_preview(
                        candidate,
                        query,
                        terms,
                    )
                )

        return "No preview available."

    @staticmethod
    def _trim_preview(
            text: str,
            query: str,
            terms: list[str],
            *,
            maximum_length: int = 180,
    ) -> str:
        collapsed = " ".join(
            text.split()
        )

        if (
                len(collapsed)
                <= maximum_length
        ):
            return collapsed

        lowered = collapsed.casefold()

        position = lowered.find(
            query
        )

        if position < 0:
            for term in terms:
                position = lowered.find(
                    term
                )

                if position >= 0:
                    break

        if position < 0:
            position = 0

        half = maximum_length // 2

        start = max(
            0,
            position - half,
            )

        end = min(
            len(collapsed),
            start + maximum_length,
            )

        snippet = collapsed[
            start:end
        ].strip()

        if start > 0:
            snippet = "… " + snippet

        if end < len(collapsed):
            snippet += " …"

        return snippet