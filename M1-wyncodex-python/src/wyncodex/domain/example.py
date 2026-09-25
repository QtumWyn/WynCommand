from dataclasses import dataclass
from uuid import uuid4


@dataclass(frozen=True)
class ExampleDraft:
    title: str
    code: str

    explanation: str | None = None
    example_type: str = "practical"
    syntax_hint: str | None = None


@dataclass(frozen=True)
class Example:
    id: int | None
    uuid: str

    entry_id: int

    title: str
    code: str

    explanation: str | None = None
    example_type: str = "practical"
    syntax_hint: str | None = None

    sort_order: int = 0

    created_at: str | None = None
    updated_at: str | None = None

    @classmethod
    def new(
            cls,
            *,
            entry_id: int,
            title: str,
            code: str,
            explanation: str | None = None,
            example_type: str = "practical",
            syntax_hint: str | None = None,
            sort_order: int = 0,
    ) -> "Example":
        return cls(
            id=None,
            uuid=str(uuid4()),
            entry_id=entry_id,
            title=title,
            code=code,
            explanation=explanation,
            example_type=example_type,
            syntax_hint=syntax_hint,
            sort_order=sort_order,
        )