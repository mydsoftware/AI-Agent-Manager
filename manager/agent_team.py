from __future__ import annotations

from agents.registry_manager import AgentRegistryManager
from agents.registry_store import AgentRegistryStore


class AgentTeam:
    """تیم پایدار Agentها را مدیریت می‌کند."""

    def __init__(self, registry_manager: AgentRegistryManager, store: AgentRegistryStore | None = None) -> None:
        self.registry_manager = registry_manager
        self.store = store or AgentRegistryStore()
        self.store.load(self.registry_manager)

    def enable(self, name: str) -> None:
        """Agent را فعال و وضعیت تیم را ذخیره می‌کند."""
        self.registry_manager.enable(name)
        self.store.save(self.registry_manager)

    def disable(self, name: str) -> None:
        """Agent را غیرفعال و وضعیت تیم را ذخیره می‌کند."""
        self.registry_manager.disable(name)
        self.store.save(self.registry_manager)

    def available(self) -> list[str]:
        """Agentهای فعال تیم را برمی‌گرداند."""
        return self.registry_manager.available()
