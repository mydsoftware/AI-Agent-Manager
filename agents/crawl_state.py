from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class CrawlState:
    """وضعیت قابل ذخیره برای ادامه Crawl پس از توقف Agent."""

    queue: list[str] = field(default_factory=list)
    visited: list[str] = field(default_factory=list)
    failed: dict[str, str] = field(default_factory=dict)

    def save(self, path: str | Path) -> None:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            json.dumps(
                {"queue": self.queue, "visited": self.visited, "failed": self.failed},
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    @classmethod
    def load(cls, path: str | Path) -> "CrawlState":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(
            queue=list(data.get("queue", [])),
            visited=list(data.get("visited", [])),
            failed=dict(data.get("failed", {})),
        )
