import json

from pathlib import Path
from typing import Any
import sqlite3

from wyncodex.domain.argument import ArgumentDraft
from wyncodex.domain.example import ExampleDraft

from wyncodex.importers.models import (
    ImportCounts,
    ImportMode,
    ImportPreview,
    ImportResult,
    ImportValidationError,
)

from wyncodex.services.category_service import (
    CategoryService,
)
from wyncodex.services.entry_service import (
    EntryService,
)
from wyncodex.services.language_service import (
    LanguageService,
)
from wyncodex.services.package_service import (
    PackageService,
)

from wyncodex.utils.text import slugify


SCHEMA_VERSION = 1


class JsonImportService:
    def __init__(
            self,
            connection: sqlite3.Connection,
            language_service: LanguageService,
            category_service: CategoryService,
            package_service: PackageService,
            entry_service: EntryService,
    ) -> None:
        self._connection = connection

        self._language_service = (
            language_service
        )

        self._category_service = (
            category_service
        )

        self._package_service = (
            package_service
        )

        self._entry_service = (
            entry_service
        )

    def preview(
            self,
            source_path: Path,
            mode: ImportMode = ImportMode.STRICT_CREATE
    ) -> ImportPreview:
        try:
            raw_text = source_path.read_text(
                encoding="utf-8"
            )
        except OSError as error:
            raise ImportValidationError(
                f"Could not read import file: "
                f"{error}"
            ) from error

        try:
            document = json.loads(
                raw_text
            )
        except json.JSONDecodeError as error:
            raise ImportValidationError(
                f"Invalid JSON at line "
                f"{error.lineno}, column "
                f"{error.colno}: "
                f"{error.msg}"
            ) from error

        if not isinstance(
                document,
                dict,
        ):
            raise ImportValidationError(
                "The JSON root must be an object."
            )

        self._validate_document(
            document
        )

        if mode is ImportMode.STRICT_CREATE:
            self._validate_database_conflicts(
                document
            )

        counts = self._count_document(
            document
        )

        return ImportPreview(
            source_path=source_path,
            document=document,
            counts=counts,
        )

    def _validate_document(
            self,
            document: dict[str, Any],
    ) -> None:
        self._check_keys(
            document,
            {
                "wyncodex_schema",
                "languages",
            },
            "$",
        )

        schema_version = document.get(
            "wyncodex_schema"
        )

        if schema_version != SCHEMA_VERSION:
            raise ImportValidationError(
                f"Unsupported WynCodex schema "
                f"{schema_version!r}. "
                f"Expected {SCHEMA_VERSION}."
            )

        languages = self._require_list(
            document.get("languages"),
            "$.languages",
        )

        seen_language_slugs: set[str] = set()

        for index, language in enumerate(
                languages
        ):
            path = (
                f"languages[{index}]"
            )

            language = self._require_object(
                language,
                path,
            )

            self._validate_language(
                language,
                path,
                seen_language_slugs,
            )

    def _validate_language(
            self,
            language: dict[str, Any],
            path: str,
            seen_language_slugs: set[str],
    ) -> None:
        self._check_keys(
            language,
            {
                "name",
                "description",
                "categories",
            },
            path,
        )

        name = self._require_text(
            language.get("name"),
            f"{path}.name",
        )

        self._optional_text(
            language.get("description"),
            f"{path}.description",
        )

        language_slug = slugify(name)

        if not language_slug:
            raise ImportValidationError(
                f"{path}.name cannot produce "
                f"a valid slug."
            )

        if language_slug in seen_language_slugs:
            raise ImportValidationError(
                f"{path}: duplicate language "
                f"slug {language_slug!r}."
            )

        seen_language_slugs.add(
            language_slug
        )

        categories = self._optional_list(
            language,
            "categories",
            path,
        )

        seen_category_slugs: set[str] = set()
        seen_entry_slugs: set[str] = set()

        for index, category in enumerate(
                categories
        ):
            category_path = (
                f"{path}.categories[{index}]"
            )

            category = self._require_object(
                category,
                category_path,
            )

            self._validate_category(
                category,
                category_path,
                seen_category_slugs,
                seen_entry_slugs,
            )

    def _validate_category(
            self,
            category: dict[str, Any],
            path: str,
            seen_category_slugs: set[str],
            seen_entry_slugs: set[str],
    ) -> None:
        self._check_keys(
            category,
            {
                "name",
                "description",
                "packages",
                "entries",
            },
            path,
        )

        name = self._require_text(
            category.get("name"),
            f"{path}.name",
        )

        self._optional_text(
            category.get("description"),
            f"{path}.description",
        )

        category_slug = slugify(name)

        if category_slug in seen_category_slugs:
            raise ImportValidationError(
                f"{path}: duplicate category "
                f"slug {category_slug!r}."
            )

        seen_category_slugs.add(
            category_slug
        )

        direct_entries = self._optional_list(
            category,
            "entries",
            path,
        )

        self._validate_entries(
            direct_entries,
            f"{path}.entries",
            seen_entry_slugs,
        )

        packages = self._optional_list(
            category,
            "packages",
            path,
        )

        seen_package_slugs: set[str] = set()

        for index, package in enumerate(
                packages
        ):
            package_path = (
                f"{path}.packages[{index}]"
            )

            package = self._require_object(
                package,
                package_path,
            )

            self._check_keys(
                package,
                {
                    "name",
                    "summary",
                    "description",
                    "entries",
                },
                package_path,
            )

            package_name = self._require_text(
                package.get("name"),
                f"{package_path}.name",
            )

            self._optional_text(
                package.get("summary"),
                f"{package_path}.summary",
            )

            self._optional_text(
                package.get("description"),
                f"{package_path}.description",
            )

            package_slug = slugify(
                package_name
            )

            if package_slug in seen_package_slugs:
                raise ImportValidationError(
                    f"{package_path}: duplicate "
                    f"package slug "
                    f"{package_slug!r}."
                )

            seen_package_slugs.add(
                package_slug
            )

            entries = self._optional_list(
                package,
                "entries",
                package_path,
            )

            self._validate_entries(
                entries,
                f"{package_path}.entries",
                seen_entry_slugs,
            )

    def _validate_entries(
            self,
            entries: list[Any],
            path: str,
            seen_entry_slugs: set[str],
    ) -> None:
        for index, entry in enumerate(
                entries
        ):
            entry_path = (
                f"{path}[{index}]"
            )

            entry = self._require_object(
                entry,
                entry_path,
            )

            self._check_keys(
                entry,
                {
                    "title",
                    "summary",
                    "signature",
                    "definition",
                    "mental_model",
                    "return_value",
                    "gotchas",
                    "notes",
                    "arguments",
                    "examples",
                },
                entry_path,
            )

            title = self._require_text(
                entry.get("title"),
                f"{entry_path}.title",
            )

            entry_slug = slugify(title)

            if not entry_slug:
                raise ImportValidationError(
                    f"{entry_path}.title cannot "
                    f"produce a valid slug."
                )

            if entry_slug in seen_entry_slugs:
                raise ImportValidationError(
                    f"{entry_path}: duplicate "
                    f"entry slug "
                    f"{entry_slug!r} "
                    f"inside this language."
                )

            seen_entry_slugs.add(
                entry_slug
            )

            for field_name in (
                    "summary",
                    "signature",
                    "definition",
                    "mental_model",
                    "return_value",
                    "gotchas",
                    "notes",
            ):
                self._optional_text(
                    entry.get(field_name),
                    f"{entry_path}.{field_name}",
                )

            arguments = self._optional_list(
                entry,
                "arguments",
                entry_path,
            )

            for argument_index, argument in enumerate(
                    arguments
            ):
                argument_path = (
                    f"{entry_path}"
                    f".arguments"
                    f"[{argument_index}]"
                )

                self._validate_argument(
                    argument,
                    argument_path,
                )

            examples = self._optional_list(
                entry,
                "examples",
                entry_path,
            )

            for example_index, example in enumerate(
                    examples
            ):
                example_path = (
                    f"{entry_path}"
                    f".examples"
                    f"[{example_index}]"
                )

                self._validate_example(
                    example,
                    example_path,
                )


    def _validate_argument(
            self,
            argument: Any,
            path: str,
    ) -> None:
        argument = self._require_object(
            argument,
            path,
        )

        self._check_keys(
            argument,
            {
                "name",
                "type",
                "description",
                "required",
                "default",
            },
            path,
        )

        self._require_text(
            argument.get("name"),
            f"{path}.name",
        )

        self._optional_text(
            argument.get("type"),
            f"{path}.type",
        )

        self._optional_text(
            argument.get("description"),
            f"{path}.description",
        )

        self._optional_text(
            argument.get("default"),
            f"{path}.default",
        )

        required = argument.get(
            "required",
            True,
        )

        if not isinstance(
                required,
                bool,
        ):
            raise ImportValidationError(
                f"{path}.required must "
                f"be true or false."
            )

    def _validate_example(
            self,
            example: Any,
            path: str,
    ) -> None:
        example = self._require_object(
            example,
            path,
        )

        self._check_keys(
            example,
            {
                "title",
                "type",
                "syntax",
                "code",
                "explanation",
            },
            path,
        )

        self._require_text(
            example.get("title"),
            f"{path}.title",
        )

        self._require_text(
            example.get("code"),
            f"{path}.code",
        )

        self._optional_text(
            example.get("type"),
            f"{path}.type",
        )

        self._optional_text(
            example.get("syntax"),
            f"{path}.syntax",
        )

        self._optional_text(
            example.get("explanation"),
            f"{path}.explanation",
        )

    @staticmethod
    def _require_object(
            value: Any,
            path: str,
    ) -> dict[str, Any]:
        if not isinstance(
                value,
                dict,
        ):
            raise ImportValidationError(
                f"{path} must be an object."
            )

        return value

    @staticmethod
    def _require_list(
            value: Any,
            path: str,
    ) -> list[Any]:
        if not isinstance(
                value,
                list,
        ):
            raise ImportValidationError(
                f"{path} must be an array."
            )

        return value

    @staticmethod
    def _require_text(
            value: Any,
            path: str,
    ) -> str:
        if not isinstance(
                value,
                str,
        ):
            raise ImportValidationError(
                f"{path} must be text."
            )

        value = value.strip()

        if not value:
            raise ImportValidationError(
                f"{path} cannot be empty."
            )

        return value

    @staticmethod
    def _optional_text(
            value: Any,
            path: str,
    ) -> None:
        if (
                value is not None
                and not isinstance(
            value,
            str,
        )
        ):
            raise ImportValidationError(
                f"{path} must be text "
                f"or null."
            )

    @staticmethod
    def _optional_list(
            container: dict[str, Any],
            key: str,
            path: str,
    ) -> list[Any]:
        value = container.get(
            key,
            [],
        )

        if not isinstance(
                value,
                list,
        ):
            raise ImportValidationError(
                f"{path}.{key} must "
                f"be an array."
            )

        return value

    @staticmethod
    def _check_keys(
            value: dict[str, Any],
            allowed: set[str],
            path: str,
    ) -> None:
        unexpected = (
                set(value)
                - allowed
        )

        if unexpected:
            bad_key = sorted(
                unexpected
            )[0]

            raise ImportValidationError(
                f"{path}: unexpected field "
                f"{bad_key!r}."
            )

    def _validate_database_conflicts(
            self,
            document: dict[str, Any],
    ) -> None:
        existing_languages = {
            language.slug
            for language
            in self._language_service
            .get_all_languages()
        }

        for index, language in enumerate(
                document["languages"]
        ):
            language_slug = slugify(
                language["name"]
            )

            if (
                    language_slug
                    in existing_languages
            ):
                raise ImportValidationError(
                    f"languages[{index}]: "
                    f"language "
                    f"{language['name']!r} "
                    f"already exists."
                )

    def _count_document(
            self,
            document: dict[str, Any],
    ) -> ImportCounts:
        languages = 0
        categories = 0
        packages = 0
        entries = 0
        arguments = 0
        examples = 0

        for language in document["languages"]:
            languages += 1

            for category in language.get(
                    "categories",
                    [],
            ):
                categories += 1

                for entry in category.get(
                        "entries",
                        [],
                ):
                    entries += 1
                    arguments += len(
                        entry.get(
                            "arguments",
                            [],
                        )
                    )
                    examples += len(
                        entry.get(
                            "examples",
                            [],
                        )
                    )

                for package in category.get(
                        "packages",
                        [],
                ):
                    packages += 1

                    for entry in package.get(
                            "entries",
                            [],
                    ):
                        entries += 1
                        arguments += len(
                            entry.get(
                                "arguments",
                                [],
                            )
                        )
                        examples += len(
                            entry.get(
                                "examples",
                                [],
                            )
                        )

        return ImportCounts(
            languages=languages,
            categories=categories,
            packages=packages,
            entries=entries,
            arguments=arguments,
            examples=examples,
        )

    def import_preview(
            self,
            preview: ImportPreview,
            mode: ImportMode = ImportMode.STRICT_CREATE,
    ) -> ImportResult:
        if mode is ImportMode.STRICT_CREATE:
            self._validate_database_conflicts(
                preview.document
            )

        try:
            self._connection.execute(
                "BEGIN IMMEDIATE"
            )

            result = self._import_document(
                preview.document,
                mode,
            )

        except Exception:
            self._connection.rollback()
            raise

        else:
            self._connection.commit()

        return result

    def _import_document(
            self,
            document: dict[str, Any],
            mode: ImportMode,
    ) -> ImportResult:
        result = ImportResult()

        for language_data in document[
            "languages"
        ]:
            language = self._resolve_language(
                language_data,
                mode,
                result,
            )

            if language.id is None:
                raise RuntimeError(
                    "Imported language has no ID."
                )

            for category_data in (
                    language_data.get(
                        "categories",
                        [],
                    )
            ):
                category = self._resolve_category(
                    language.id,
                    category_data,
                    mode,
                    result,
                )

                if category.id is None:
                    raise RuntimeError(
                        "Imported category "
                        "has no ID."
                    )

                for entry_data in (
                        category_data.get(
                            "entries",
                            [],
                        )
                ):
                    self._import_entry(
                        entry_data,
                        language_id=language.id,
                        category_id=category.id,
                        package_id=None,
                        default_syntax_hint=(
                            language.slug
                        ),
                        mode=mode,
                        result=result,
                    )

                for package_data in (
                        category_data.get(
                            "packages",
                            [],
                        )
                ):
                    package = self._resolve_package(
                        category.id,
                        package_data,
                        mode,
                        result,
                    )

                    if package.id is None:
                        raise RuntimeError(
                            "Imported package "
                            "has no ID."
                        )

                    for entry_data in (
                            package_data.get(
                                "entries",
                                [],
                            )
                    ):
                        self._import_entry(
                            entry_data,
                            language_id=language.id,
                            category_id=category.id,
                            package_id=package.id,
                            default_syntax_hint=(
                                language.slug
                            ),
                            mode=mode,
                            result=result,
                        )

        return result


    def _import_entry(
            self,
            entry_data: dict[str, Any],
            *,
            language_id: int,
            category_id: int,
            package_id: int | None,
            default_syntax_hint: str,
            mode: ImportMode,
            result: ImportResult,
    ) -> None:
        entry_slug = slugify(
            entry_data["title"]
        )

        if (
                mode
                is ImportMode.MERGE_SKIP_EXISTING
        ):
            existing = (
                self._entry_service
                .get_entry_by_slug(
                    language_id,
                    entry_slug,
                )
            )

            if existing is not None:
                result.entries_skipped += 1

                return

        arguments = [
            ArgumentDraft(
                name=argument["name"],
                type_text=argument.get(
                    "type"
                ),
                description=argument.get(
                    "description"
                ),
                required=argument.get(
                    "required",
                    True,
                ),
                default_value=argument.get(
                    "default"
                ),
            )
            for argument
            in entry_data.get(
                "arguments",
                [],
            )
        ]

        examples = [
            ExampleDraft(
                title=example["title"],
                code=example["code"],
                explanation=example.get(
                    "explanation"
                ),
                example_type=(
                        example.get("type")
                        or "practical"
                ),
                syntax_hint=(
                        example.get("syntax")
                        or default_syntax_hint
                ),
            )
            for example
            in entry_data.get(
                "examples",
                [],
            )
        ]

        self._entry_service.create_entry(
            category_id=category_id,
            package_id=package_id,

            title=entry_data["title"],
            summary=entry_data.get(
                "summary"
            ),
            signature=entry_data.get(
                "signature"
            ),
            definition=entry_data.get(
                "definition"
            ),
            mental_model=entry_data.get(
                "mental_model"
            ),
            return_value=entry_data.get(
                "return_value"
            ),
            gotchas=entry_data.get(
                "gotchas"
            ),
            notes=entry_data.get(
                "notes"
            ),

            arguments=arguments,
            examples=examples,

            commit=False,
        )

        result.entries_created += 1

        result.arguments_created += len(
            arguments
        )
        
        result.examples_created += len(
            examples
        )

    def _resolve_language(
            self,
            language_data: dict[str, Any],
            mode: ImportMode,
            result: ImportResult,
    ):
        slug = slugify(
            language_data["name"]
        )

        if (
                mode
                is ImportMode.MERGE_SKIP_EXISTING
        ):
            existing = (
                self._language_service
                .get_language_by_slug(
                    slug
                )
            )

            if existing is not None:
                result.languages_reused += 1

                return existing

        created = (
            self._language_service
            .create_language(
                name=language_data["name"],
                description=(
                    language_data.get(
                        "description"
                    )
                ),
                commit=False,
            )
        )

        result.languages_created += 1

        return created

    def _resolve_category(
            self,
            language_id: int,
            category_data: dict[str, Any],
            mode: ImportMode,
            result: ImportResult,
    ):
        slug = slugify(
            category_data["name"]
        )

        if (
                mode
                is ImportMode.MERGE_SKIP_EXISTING
        ):
            existing = (
                self._category_service
                .get_category_by_slug(
                    language_id,
                    slug,
                )
            )

            if existing is not None:
                result.categories_reused += 1

                return existing

        created = (
            self._category_service
            .create_category(
                language_id=language_id,
                name=category_data["name"],
                description=(
                    category_data.get(
                        "description"
                    )
                ),
                commit=False,
            )
        )

        result.categories_created += 1

        return created

    def _resolve_package(
            self,
            category_id: int,
            package_data: dict[str, Any],
            mode: ImportMode,
            result: ImportResult,
    ):
        slug = slugify(
            package_data["name"]
        )

        if (
                mode
                is ImportMode.MERGE_SKIP_EXISTING
        ):
            existing = (
                self._package_service
                .get_package_by_slug(
                    category_id,
                    slug,
                )
            )

            if existing is not None:
                result.packages_reused += 1

                return existing

        created = (
            self._package_service
            .create_package(
                category_id=category_id,
                name=package_data["name"],
                summary=package_data.get(
                    "summary"
                ),
                description=(
                    package_data.get(
                        "description"
                    )
                ),
                commit=False,
            )
        )

        result.packages_created += 1

        return created