from dataclasses import dataclass
from uuid import uuid4


@dataclass(frozen=True)
class Category:
    id: int | None
    uuid: str

    language_id: int

    name: str
    slug: str

    description: str | None = None

    sort_order: int = 0

    created_at: str | None = None
    updated_at: str | None = None

    @classmethod
    def new(
            cls,
            *,
            language_id: int,
            name: str,
            slug: str,
            description: str | None = None,
    ) -> "Category":
        return cls(
            id=None,
            uuid=str(uuid4()),
            language_id=language_id,
            name=name,
            slug=slug,
            description=description,
        )