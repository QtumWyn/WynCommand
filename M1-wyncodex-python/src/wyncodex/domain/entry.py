from dataclasses import dataclass
from uuid import uuid4


@dataclass(frozen=True)
class Entry:
    id: int | None
    uuid: str

    language_id: int
    category_id: int
    package_id: int | None

    title: str
    slug: str

    summary: str | None = None
    signature: str | None = None
    definition: str | None = None
    mental_model: str | None = None
    return_value: str | None = None
    gotchas: str | None = None
    notes: str | None = None

    sort_order: int = 0

    created_at: str | None = None
    updated_at: str | None = None

    @classmethod
    def new(
        cls,
        *,
        language_id: int,
        category_id: int,
        title: str,
        slug: str,
        package_id: int | None = None,
        summary: str | None = None,
        signature: str | None = None,
        definition: str | None = None,
        mental_model: str | None = None,
        return_value: str | None = None,
        gotchas: str | None = None,
        notes: str | None = None,
    ) -> "Entry":
        return cls(
            id=None,
            uuid=str(uuid4()),
            language_id=language_id,
            category_id=category_id,
            package_id=package_id,
            title=title,
            slug=slug,
            summary=summary,
            signature=signature,
            definition=definition,
            mental_model=mental_model,
            return_value=return_value,
            gotchas=gotchas,
            notes=notes,
        )