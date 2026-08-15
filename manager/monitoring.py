from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any


@dataclass
class HealthSnapshot:
    status: str
    active_tasks: int
    completed_tasks: int
    failed_tasks: int
    timestamp: str


class Monitor:
    def __init__(self) -> None:
        self.active = 0
        self.completed = 0
        self.failed = 0

    def task_started(self) -> None:
        self.active += 1

    def task_completed(self) -> None:
        self.active = max(0, self.active - 1)
        self.completed += 1

    def task_failed(self) -> None:
        self.active = max(0, self.active - 1)
        self.failed += 1

    def health(self) -> dict[str, Any]:
        status = "healthy" if self.failed == 0 else "degraded"
        return asdict(HealthSnapshot(status, self.active, self.completed, self.failed, datetime.now(timezone.utc).isoformat()))
