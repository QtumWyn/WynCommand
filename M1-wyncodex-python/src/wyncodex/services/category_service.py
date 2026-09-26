from wyncodex.domain.category import Category
from wyncodex.repositories.category_repository import (
    CategoryRepository,
)
from wyncodex.repositories.language_repository import (
    LanguageRepository,
)
from wyncodex.utils.text import slugify


class CategoryService:
    def __init__(
            self,
            category_repository: CategoryRepository,
            language_repository: LanguageRepository,
    ) -> None:
        self._category_repository = category_repository
        self._language_repository = language_repository

    def create_category(
            self,
            *,
            language_id: int,
            name: str,
            slug: str | None = None,
            description: str | None = None,
            commit: bool = True,
    ) -> Category:
        name = name.strip()

        if not name:
            raise ValueError(
                "Category cannot be empty."
            )

        resolved_slug = slugify(
            slug if slug else name
        )

        if not resolved_slug:
            raise ValueError(
                "Category could not produce a valid slug."
            )

        language = (
            self._language_repository
            .get_by_id(language_id)
        )

        if language is None:
            raise ValueError(
                "The selected language does not exist."
            )

        existing = (
            self._category_repository
            .get_by_slug(
                language_id,
                resolved_slug,
            )
        )

        if existing is not None:
            raise ValueError(
                f"A category with the slug "
                f"{resolved_slug!r} already exists "
                f"for {language.name}."
            )

        category = Category.new(
            language_id=language_id,
            name=name,
            slug=resolved_slug,
            description=description,
        )

        return self._category_repository.create(
            category,
            commit=commit,
        )

    def get_categories_for_language(
            self,
            language_id: int,
    ) -> list[Category]:
        return (
            self._category_repository
            .get_for_language(language_id)
        )

    def get_category_by_id(
            self,
            category_id: int,
    ) -> Category | None:
        return (
            self._category_repository
            .get_by_id(category_id)
        )

    def get_category_by_slug(
            self,
            language_id: int,
            slug: str,
    ) -> Category | None:
        return (
            self._category_repository
            .get_by_slug(
                language_id,
                slug,
            )
        )