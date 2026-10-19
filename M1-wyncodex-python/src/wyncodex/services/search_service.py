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
            limit: int = 50,
    ) -> list[SearchResult]:
        query = query.strip()

        if len(query) < 2:
            return []

        return self._repository.search(
            query,
            limit=limit,
        )