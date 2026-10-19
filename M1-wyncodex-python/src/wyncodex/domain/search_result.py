from dataclasses import dataclass


@dataclass(frozen=True)
class SearchResult:
    entry_id: int

    title: str
    entry_kind: str

    language_name: str
    category_name: str
    package_name: str | None

    entry_path: str
    full_path: str

    summary: str | None
    preview: str

    score: int