from wyncodex.domain.package import Package
from wyncodex.repositories.category_repository import (
    CategoryRepository,
)
from wyncodex.repositories.package_repository import (
    PackageRepository,
)
from wyncodex.utils.text import slugify


class PackageService:
    def __init__(
            self,
            package_repository: PackageRepository,
            category_repository: CategoryRepository,
    ) -> None:
        self._package_repository = package_repository
        self._category_repository = category_repository

    def create_package(
            self,
            *,
            category_id: int,
            name: str,
            slug: str | None = None,
            summary: str | None = None,
            description: str | None = None,
            commit: bool = True,
    ) -> Package:
        name = name.strip()

        if not name:
            raise ValueError(
                "Package name cannot be empty."
            )

        resolved_slug = slugify(
            slug if slug else name
        )

        if not resolved_slug:
            raise ValueError(
                "Package name could not produce a valid slug."
            )

        summary = summary.strip() if summary else None

        description = (
            description.strip()
            if description
            else None
        )

        category = (
            self._category_repository
            .get_by_id(category_id)
        )

        if category is None:
            raise ValueError(
                "The selected category does not exist."
            )

        existing = (
            self._package_repository
            .get_by_slug(
                category_id,
                resolved_slug,
            )
        )

        if existing is not None:
            raise ValueError(
                f"A package with the slug "
                f"{resolved_slug!r} already exists "
                f"in {category.name}."
            )

        package = Package.new(
            category_id=category_id,
            name=name,
            slug=resolved_slug,
            summary=summary,
            description=description,
        )

        return self._package_repository.create(
            package,
            commit=commit,
        )

    def get_packages_for_category(
            self,
            category_id: int,
    ) -> list[Package]:
        return (
            self._package_repository
            .get_for_category(category_id)
        )

    def get_package_by_id(
            self,
            package_id: int,
    ) -> Package | None:
        return (
            self._package_repository
            .get_by_id(package_id)
        )

    def get_package_by_slug(
            self,
            category_id: int,
            slug: str,
    ) -> Package | None:
        return (
            self._package_repository
            .get_by_slug(
                category_id,
                slug,
            )
        )