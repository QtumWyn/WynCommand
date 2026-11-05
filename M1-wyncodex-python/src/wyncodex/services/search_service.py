from wyncodex.domain.search_result import (
    SearchResult,
)

from wyncodex.repositories.search_repository import (
    SearchRepository,
)


class SearchService:
    def __init__(
            self,
            repository: SearchRepository,
    ) -> None:
        self._repository = repository

    def search(
            self,
            query: str,
            *,
            language_id: int | None = None,
            limit: int = 50,
            assembly_track: int | None = None,
            language_kind: str | None = None,
    ) -> list[SearchResult]:
        query = query.strip()

        if len(query) < (1 if language_kind == "natural" else 2):
            return []

        return self._repository.search(
            query,
            language_id=language_id,
            limit=limit,
            assembly_track=assembly_track,
            language_kind=language_kind,
        )