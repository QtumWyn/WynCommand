from dataclasses import dataclass
from uuid import uuid4


@dataclass(frozen=True)
class ArgumentDraft:
    name: str
    type_text: str | None = None
    description: str | None = None
    required: bool = True
    default_value: str | None = None


@dataclass(frozen=True)
class Argument:
    id: int | None
    uuid: str

    entry_id: int
    position: int

    name: str
    type_text: str | None = None
    description: str | None = None

    required: bool = True
    default_value: str | None = None

    created_at: str | None = None
    updated_at: str | None = None

    @classmethod
    def new(
            cls,
            *,
            entry_id: int,
            position: int,
            name: str,
            type_text: str | None = None,
            description: str | None = None,
            required: bool = True,
            default_value: str | None = None,
    ) -> "Argument":
        return cls(
            id=None,
            uuid=str(uuid4()),
            entry_id=entry_id,
            position=position,
            name=name,
            type_text=type_text,
            description=description,
            required=required,
            default_value=default_value,
        )