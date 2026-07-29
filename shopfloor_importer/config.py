from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .model import FieldSpec


@dataclass(frozen=True)
class Config:
    website_url: str
    integration: str
    auth: str
    form_url: str | None
    submit_selector: str | None
    success_selector: str | None
    header_row: int
    row_key_column: str | None
    record_selector: str | None
    machine_selector: str | None
    allowed_machines: tuple[str, ...]
    fields: tuple[FieldSpec, ...]


def load_config(path: str | Path) -> Config:
    raw: dict[str, Any] = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    fields = tuple(
        FieldSpec(
            column=item["column"], target=item["target"],
            required=item.get("required", False), kind=item.get("type", "string"),
            choices=tuple(str(choice) for choice in item.get("choices", ())),
            enable_selector=item.get("enable_selector"),
        )
        for item in raw["fields"]
    )
    return Config(
        website_url=raw["website_url"].rstrip("/"),
        integration=raw["integration"], auth=raw.get("authentication", "none"),
        form_url=raw.get("form_url"),
        submit_selector=raw.get("submit_selector"),
        success_selector=raw.get("success_selector"), fields=fields,
        header_row=int(raw.get("header_row", 1)),
        row_key_column=raw.get("row_key_column"),
        record_selector=raw.get("record_selector"),
        machine_selector=raw.get("machine_selector"),
        allowed_machines=tuple(str(value).upper() for value in raw.get("allowed_machines", ())),
    )
