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
            commit: bool = True,
            language_kind: str = "programming",
    ) -> Language:
        if language_kind not in ("programming", "natural"):
            raise ValueError("Invalid language kind.")
        name = name.strip()

        if not name:
            raise ValueError(
                "Language name cannot be empty."
            )

        resolved_slug = slugify(slug if slug else name)
        if language_kind == "natural":
            from wyncodex.utils.text import unicode_slugify
            resolved_slug = unicode_slugify(slug if slug else name)
            if resolved_slug:
                resolved_slug = "natural-" + resolved_slug

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
            language_kind=language_kind,
        )

        return self._repository.create(
            language,
            commit=commit,
        )

    def get_all_languages(self, language_kind: str | None = None) -> list[Language]:
        return self._repository.get_all(language_kind)

    def get_language_by_id(
            self,
            language_id: int,
    ) -> Language | None:
        return self._repository.get_by_id(language_id)

    def get_language_by_slug(
            self,
            slug: str,
    ) -> Language | None:
        return self._repository.get_by_slug(
            slug
        )

    def update_language(self, language_id: int, *, name: str, description: str | None = None) -> Language:
        if not name.strip():
            raise ValueError("Language name cannot be empty.")
        if self._repository.get_by_id(language_id) is None:
            raise ValueError("Language no longer exists.")
        return self._repository.update(language_id,name.strip(),description)
