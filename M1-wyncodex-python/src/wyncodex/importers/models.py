from dataclasses import dataclass
from pathlib import Path
from typing import Any
from enum import Enum


class ImportValidationError(ValueError):
    pass

class ImportMode(Enum):
    STRICT_CREATE = "strict_create"
    MERGE_SKIP_EXISTING = "merge_skip_existing"

@dataclass(frozen=True)
class ImportCounts:
    languages: int = 0
    categories: int = 0
    packages: int = 0
    entries: int = 0
    arguments: int = 0
    examples: int = 0


@dataclass(frozen=True)
class ImportPreview:
    source_path: Path
    document: dict[str, Any]
    counts: ImportCounts

@dataclass
class ImportResult:
    languages_created: int = 0
    categories_created: int = 0
    packages_created: int = 0
    entries_created: int = 0
    arguments_created: int = 0
    examples_created: int = 0

    languages_reused: int = 0
    categories_reused: int = 0
    packages_reused: int = 0

    entries_skipped: int = 0