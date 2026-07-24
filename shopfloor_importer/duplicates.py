import hashlib
import json
from pathlib import Path
from typing import Any


def fingerprint(mapped: dict[str, Any]) -> str:
    canonical = json.dumps(mapped, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode()).hexdigest()


class SubmissionLedger:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.seen: set[str] = set()
        if self.path.exists():
            self.seen = set(json.loads(self.path.read_text(encoding="utf-8")))

    def contains(self, values: dict[str, Any]) -> bool:
        return fingerprint(values) in self.seen

    def add(self, values: dict[str, Any]) -> None:
        self.seen.add(fingerprint(values))
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(json.dumps(sorted(self.seen), indent=2), encoding="utf-8")
        temporary.replace(self.path)
