from wyncodex.domain.entry import Entry
from wyncodex.repositories.category_repository import (
    CategoryRepository,
)
from wyncodex.repositories.entry_repository import (
    EntryRepository,
)
from wyncodex.repositories.package_repository import (
    PackageRepository,
)
from wyncodex.utils.text import (
    clean_optional_text,
    slugify,
)
from wyncodex.domain.argument import (
    Argument,
    ArgumentDraft,
)
from wyncodex.domain.example import (
    Example,
    ExampleDraft,
)

from wyncodex.repositories.argument_repository import (
    ArgumentRepository,
)
from wyncodex.repositories.example_repository import (
    ExampleRepository,
)


class EntryService:
    def __init__(
            self,
            entry_repository: EntryRepository,
            category_repository: CategoryRepository,
            package_repository: PackageRepository,
            argument_repository: ArgumentRepository,
            example_repository: ExampleRepository,
    ) -> None:
        self._entry_repository = entry_repository
        self._category_repository = category_repository
        self._package_repository = package_repository
        self._argument_repository = argument_repository
        self._example_repository = example_repository

    def create_entry(
            self,
            *,
            category_id: int,
            title: str,
            package_id: int | None = None,
            slug: str | None = None,
            summary: str | None = None,
            signature: str | None = None,
            definition: str | None = None,
            mental_model: str | None = None,
            return_value: str | None = None,
            gotchas: str | None = None,
            notes: str | None = None,
            arguments: list[ArgumentDraft] | None = None,
            examples: list[ExampleDraft] | None = None,
    ) -> Entry:
        title = title.strip()

        if not title:
            raise ValueError(
                "Entry title cannot be empty."
            )

        category = (
            self._category_repository
            .get_by_id(category_id)
        )

        if category is None:
            raise ValueError(
                "The selected category does not exist."
            )

        if package_id is not None:
            package = (
                self._package_repository
                .get_by_id(package_id)
            )

            if package is None:
                raise ValueError(
                    "The selected package does not exist."
                )

            if package.category_id != category_id:
                raise ValueError(
                    "The selected package does not "
                    "belong to the selected category."
                )

        resolved_slug = slugify(
            slug if slug else title
        )

        if not resolved_slug:
            raise ValueError(
                "Entry title could not produce "
                "a valid slug."
            )

        existing = (
            self._entry_repository
            .get_by_slug(
                category.language_id,
                resolved_slug,
            )
        )

        if existing is not None:
            raise ValueError(
                f"An entry with the slug "
                f"{resolved_slug!r} already exists "
                f"in this language."
            )

        entry = Entry.new(
            language_id=category.language_id,
            category_id=category_id,
            package_id=package_id,
            title=title,
            slug=resolved_slug,
            summary=clean_optional_text(summary),
            signature=clean_optional_text(signature),
            definition=clean_optional_text(definition),
            mental_model=clean_optional_text(
                mental_model
            ),
            return_value=clean_optional_text(
                return_value
            ),
            gotchas=clean_optional_text(gotchas),
            notes=clean_optional_text(notes),
        )

        created_entry = (
            self._entry_repository.create(
                entry
            )
        )

        if created_entry.id is None:
            raise RuntimeError(
                "Created entry has no database ID."
            )

        try:
            for position, draft in enumerate(
                    arguments or []
            ):
                name = draft.name.strip()

                if not name:
                    raise ValueError(
                        f"Argument {position + 1} "
                        f"needs a name."
                    )

                argument = Argument.new(
                    entry_id=created_entry.id,
                    position=position,
                    name=name,
                    type_text=clean_optional_text(
                        draft.type_text
                    ),
                    description=clean_optional_text(
                        draft.description
                    ),
                    required=draft.required,
                    default_value=clean_optional_text(
                        draft.default_value
                    ),
                )

                self._argument_repository.create(
                    argument
                )

            for sort_order, draft in enumerate(
                    examples or []
            ):
                title = draft.title.strip()
                code = draft.code.strip()

                if not title:
                    raise ValueError(
                        f"Example {sort_order + 1} "
                        f"needs a title."
                    )

                if not code:
                    raise ValueError(
                        f"Example {sort_order + 1} "
                        f"needs some code."
                    )

                example = Example.new(
                    entry_id=created_entry.id,
                    title=title,
                    code=code,
                    explanation=clean_optional_text(
                        draft.explanation
                    ),
                    example_type=(
                            clean_optional_text(
                                draft.example_type
                            )
                            or "practical"
                    ),
                    syntax_hint=clean_optional_text(
                        draft.syntax_hint
                    ),
                    sort_order=sort_order,
                )

                self._example_repository.create(
                    example
                )

        except Exception:
            self._entry_repository.delete(
                created_entry.id
            )
            raise

        return created_entry

    def get_entry_by_id(
            self,
            entry_id: int,
    ) -> Entry | None:
        return self._entry_repository.get_by_id(
            entry_id
        )

    def get_entries_for_package(
            self,
            package_id: int,
    ) -> list[Entry]:
        return (
            self._entry_repository
            .get_for_package(package_id)
        )

    def get_direct_entries_for_category(
            self,
            category_id: int,
    ) -> list[Entry]:
        return (
            self._entry_repository
            .get_direct_for_category(
                category_id
            )
        )

    def get_arguments_for_entry(
            self,
            entry_id: int,
    ) -> list[Argument]:
        return (
            self._argument_repository
            .get_for_entry(entry_id)
        )


    def get_examples_for_entry(
            self,
            entry_id: int,
    ) -> list[Example]:
        return (
            self._example_repository
            .get_for_entry(entry_id)
        )

    def update_entry(
            self,
            *,
            entry_id: int,
            title: str,
            summary: str | None = None,
            signature: str | None = None,
            definition: str | None = None,
            mental_model: str | None = None,
            return_value: str | None = None,
            gotchas: str | None = None,
            notes: str | None = None,
            arguments: list[ArgumentDraft] | None = None,
            examples: list[ExampleDraft] | None = None,
    ) -> Entry:
        existing = (
            self._entry_repository
            .get_by_id(entry_id)
        )

        if existing is None:
            raise ValueError(
                "The entry does not exist."
            )

        title = title.strip()

        if not title:
            raise ValueError(
                "Entry title cannot be empty."
            )

        resolved_slug = slugify(title)

        if not resolved_slug:
            raise ValueError(
                "Entry title could not produce "
                "a valid slug."
            )

        slug_owner = (
            self._entry_repository
            .get_by_slug(
                existing.language_id,
                resolved_slug,
            )
        )

        if (
                slug_owner is not None
                and slug_owner.id != entry_id
        ):
            raise ValueError(
                f"Another entry already uses "
                f"the slug {resolved_slug!r}."
            )

        argument_drafts = arguments or []
        example_drafts = examples or []

        # Validate everything before touching
        # existing database rows.
        for position, draft in enumerate(
                argument_drafts
        ):
            if not draft.name.strip():
                raise ValueError(
                    f"Argument {position + 1} "
                    f"needs a name."
                )

        for position, draft in enumerate(
                example_drafts
        ):
            if not draft.title.strip():
                raise ValueError(
                    f"Example {position + 1} "
                    f"needs a title."
                )

            if not draft.code.strip():
                raise ValueError(
                    f"Example {position + 1} "
                    f"needs some code."
                )

        updated_entry = Entry(
            id=existing.id,
            uuid=existing.uuid,
            language_id=existing.language_id,
            category_id=existing.category_id,
            package_id=existing.package_id,

            title=title,
            slug=resolved_slug,

            summary=clean_optional_text(
                summary
            ),
            signature=clean_optional_text(
                signature
            ),
            definition=clean_optional_text(
                definition
            ),
            mental_model=clean_optional_text(
                mental_model
            ),
            return_value=clean_optional_text(
                return_value
            ),
            gotchas=clean_optional_text(
                gotchas
            ),
            notes=clean_optional_text(
                notes
            ),

            sort_order=existing.sort_order,
            created_at=existing.created_at,
            updated_at=existing.updated_at,
        )

        updated_entry = (
            self._entry_repository.update(
                updated_entry
            )
        )

        # Replace the child collections with
        # whatever currently exists in the editor.
        self._argument_repository.delete_for_entry(
            entry_id
        )

        self._example_repository.delete_for_entry(
            entry_id
        )

        for position, draft in enumerate(
                argument_drafts
        ):
            argument = Argument.new(
                entry_id=entry_id,
                position=position,
                name=draft.name.strip(),

                type_text=clean_optional_text(
                    draft.type_text
                ),

                description=clean_optional_text(
                    draft.description
                ),

                required=draft.required,

                default_value=clean_optional_text(
                    draft.default_value
                ),
            )

            self._argument_repository.create(
                argument
            )

        for sort_order, draft in enumerate(
                example_drafts
        ):
            example = Example.new(
                entry_id=entry_id,
                title=draft.title.strip(),
                code=draft.code.strip(),

                explanation=clean_optional_text(
                    draft.explanation
                ),

                example_type=(
                        clean_optional_text(
                            draft.example_type
                        )
                        or "practical"
                ),

                syntax_hint=clean_optional_text(
                    draft.syntax_hint
                ),

                sort_order=sort_order,
            )

            self._example_repository.create(
                example
            )

        return updated_entry