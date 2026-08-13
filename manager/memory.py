from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Memory:
    """حافظه ساده اجرای Manager برای نگهداری رویدادها و نتایج."""

    events: list[dict[str, Any]] = field(default_factory=list)

    def add(self, event: str, data: Any = None) -> None:
        """یک رویداد را در حافظه ثبت می‌کند."""
        self.events.append({"event": event, "data": data})

    def all(self) -> list[dict[str, Any]]:
        """تمام رویدادهای ثبت‌شده را برمی‌گرداند."""
        return list(self.events)
