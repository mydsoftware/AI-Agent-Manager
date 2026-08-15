from __future__ import annotations

from dataclasses import dataclass
from typing import Type

from .base_agent import BaseAgent
from .registry import SpecialistRegistry


@dataclass
class AgentRecord:
    """اطلاعات مدیریتی یک ایجنت ثبت‌شده."""

    name: str
    enabled: bool = True
    description: str = ""


class AgentRegistryManager:
    """مدیریت چرخه حیات ایجنت‌ها در Registry."""

    def __init__(self, registry: SpecialistRegistry) -> None:
        self.registry = registry
        self._records: dict[str, AgentRecord] = {
            name: AgentRecord(name=name) for name in registry.names()
        }

    def register(self, agent_class: Type[BaseAgent], description: str = "") -> AgentRecord:
        """یک ایجنت جدید را ثبت و فعال می‌کند."""
        self.registry.register(agent_class)
        record = AgentRecord(name=agent_class.name, enabled=True, description=description)
        self._records[agent_class.name] = record
        return record

    def enable(self, name: str) -> None:
        """ایجنت را فعال می‌کند."""
        self._require(name).enabled = True

    def disable(self, name: str) -> None:
        """ایجنت را غیرفعال می‌کند."""
        self._require(name).enabled = False

    def is_enabled(self, name: str) -> bool:
        """وضعیت فعال بودن ایجنت را برمی‌گرداند."""
        return self._require(name).enabled

    def available(self) -> list[str]:
        """نام ایجنت‌های فعال را برمی‌گرداند."""
        return sorted(name for name, record in self._records.items() if record.enabled)

    def remove(self, name: str) -> None:
        """یک ایجنت را از Registry مدیریتی حذف می‌کند."""
        self._require(name)
        self._records.pop(name)
        self.registry._agents.pop(name, None)

    def _require(self, name: str) -> AgentRecord:
        if name not in self._records:
            raise KeyError(f"ایجنت «{name}» ثبت نشده است.")
        return self._records[name]
