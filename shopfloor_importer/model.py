from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class FieldSpec:
    column: str
    target: str
    required: bool = False
    kind: str = "string"
    choices: tuple[str, ...] = ()
    enable_selector: str | None = None


@dataclass
class RowRecord:
    row_number: int
    values: dict[str, Any]
    mapped: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return not self.errors
