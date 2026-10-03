from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class GrowthAction:
    """یک اقدام بیرونی قابل اجرای Growth Engine."""

    name: str
    phase: str
    payload: dict[str, Any]


@dataclass(frozen=True)
class GrowthActionResult:
    status: str
    action: str
    phase: str
    external_execution: bool
    data: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "action": self.action,
            "phase": self.phase,
            "external_execution": self.external_execution,
            "data": self.data,
        }


class GrowthAdapter(Protocol):
    def execute(self, action: GrowthAction) -> dict[str, Any]: ...


class DryRunAdapter:
    """Adapter امن پیش‌فرض؛ بدون اتصال واقعی هیچ اقدام خارجی انجام نمی‌دهد."""

    def execute(self, action: GrowthAction) -> dict[str, Any]:
        return GrowthActionResult(
            status="planned",
            action=action.name,
            phase=action.phase,
            external_execution=False,
            data={"payload": action.payload},
        ).as_dict()


class GrowthActionRegistry:
    """Registry قابل توسعه برای اتصال سرویس‌های واقعی بدون تغییر Agentها."""

    DEFAULT_ACTIONS = (
        "collect_search_console",
        "collect_analytics",
        "create_lead",
        "qualify_lead",
        "send_follow_up",
        "publish_content",
        "launch_campaign",
        "record_sale",
    )

    def __init__(self, adapters: dict[str, GrowthAdapter] | None = None) -> None:
        self._adapters: dict[str, GrowthAdapter] = dict(adapters or {})

    def register(self, action_name: str, adapter: GrowthAdapter) -> None:
        if not action_name.strip():
            raise ValueError("نام action نمی‌تواند خالی باشد.")
        self._adapters[action_name] = adapter

    def has_adapter(self, action_name: str) -> bool:
        return action_name in self._adapters

    def execute(self, action: GrowthAction) -> dict[str, Any]:
        adapter = self._adapters.get(action.name, DryRunAdapter())
        return adapter.execute(action)

    def execute_many(self, actions: list[GrowthAction]) -> list[dict[str, Any]]:
        return [self.execute(action) for action in actions]
