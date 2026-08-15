from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class AuditEvent:
    event: str
    task_id: str | None
    status: str
    detail: Any
    timestamp: str


class AuditLog:
    def __init__(self) -> None:
        self.events: list[AuditEvent] = []

    def record(self, event: str, task_id: str | None = None, status: str = "info", detail: Any = None) -> AuditEvent:
        item = AuditEvent(event, task_id, status, detail, datetime.now(timezone.utc).isoformat())
        self.events.append(item)
        return item

    def export(self) -> list[dict[str, Any]]:
        return [asdict(event) for event in self.events]
