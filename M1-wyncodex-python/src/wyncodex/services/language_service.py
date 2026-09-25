from wyncodex.domain.language import Language
from wyncodex.repositories.language_repository import LanguageRepository
from wyncodex.utils.text import slugify


class LanguageService:
    def __init__(self, repository: LanguageRepository) -> None:
        self._repository = repository

    def create_language(
            self,
            *,
            name: str,
            description: str | None = None,
            slug: str | None = None,
    ) -> Language:
        name = name.strip()

        if not name:
            raise ValueError(
                "Language name cannot be empty."
            )

        resolved_slug = slugify(
            slug if slug else name
        )

        if not resolved_slug:
            raise ValueError(
                "Language name could not produce a valid slug."
            )

        existing = self._repository.get_by_slug(
            resolved_slug
        )

        if existing is not None:
            raise ValueError(
                f"A language with the slug {resolved_slug!r} already exists."
            )

        language = Language.new(
            name=name,
            slug=resolved_slug,
            description=description,
        )

        return self._repository.create(language)

    def get_all_languages(self) -> list[Language]:
        return self._repository.get_all()

    def get_language_by_id(
            self,
            language_id: int,
    ) -> Language | None:
        return self._repository.get_by_id(language_id)