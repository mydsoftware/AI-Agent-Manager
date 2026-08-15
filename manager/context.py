from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentContext:
    """محل اشتراک خروجی ایجنت‌ها در یک اجرای Manager."""

    values: dict[str, Any] = field(default_factory=dict)

    def set(self, key: str, value: Any) -> None:
        """یک خروجی را در زمینه مشترک ثبت می‌کند."""
        self.values[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """یک خروجی ثبت‌شده را دریافت می‌کند."""
        return self.values.get(key, default)
