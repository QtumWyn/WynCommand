from dataclasses import dataclass
from uuid import uuid4

@dataclass(frozen=True)
class Language:
    id: int | None
    uuid: str

    name: str
    slug: str

    description: str | None = None
    color: str | None = None
    icon_name: str | None = None

    is_enabled: bool = True
    sort_order: int = 0
    created_at: str | None = None
    updated_at: str | None = None

    @classmethod
    def new(
            cls,
            *,
            name: str,
            slug: str,
            description: str | None = None,
    ) -> "Language":
        return cls(
            id=None,
            uuid=str(uuid4()),
            name=name,
            slug=slug,
            description=description,
        )