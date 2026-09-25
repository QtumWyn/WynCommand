from dataclasses import dataclass
from uuid import uuid4


@dataclass(frozen=True)
class Package:
    id: int | None
    uuid: str

    category_id: int

    name: str
    slug: str

    summary: str | None = None
    description: str | None = None

    sort_order: int = 0

    created_at: str | None = None
    updated_at: str | None = None

    @classmethod
    def new(
            cls,
            *,
            category_id: int,
            name: str,
            slug: str,
            summary: str | None = None,
            description: str | None = None,
    ) -> "Package":
        return cls(
            id=None,
            uuid=str(uuid4()),
            category_id=category_id,
            name=name,
            slug=slug,
            summary=summary,
            description=description,
        )