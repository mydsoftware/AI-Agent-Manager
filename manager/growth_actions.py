from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class GrowthAction:
    name: str
    phase: str
    payload: dict[str, Any]


class GrowthAdapter(Protocol):
    def execute(self, action: GrowthAction) -> dict[str, Any]: ...


class DryRunAdapter:
    """Adapter امن پیش‌فرض؛ بدون credential هیچ اقدام خارجی انجام نمی‌دهد."""

    def execute(self, action: GrowthAction) -> dict[str, Any]:
        return {
            "status": "planned",
            "action": action.name,
            "phase": action.phase,
            "payload": action.payload,
            "external_execution": False,
        }


class GrowthActionRegistry:
    def __init__(self) -> None:
        self._adapters: dict[str, GrowthAdapter] = {}

    def register(self, action_name: str, adapter: GrowthAdapter) -> None:
        self._adapters[action_name] = adapter

    def execute(self, action: GrowthAction) -> dict[str, Any]:
        adapter = self._adapters.get(action.name, DryRunAdapter())
        return adapter.execute(action)
