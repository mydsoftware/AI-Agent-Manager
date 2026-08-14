from __future__ import annotations

from agents.registry_manager import AgentRegistryManager


class AgentGovernance:
    """لایه سیاست‌گذاری برای انتخاب ایجنت‌های قابل استفاده توسط Manager."""

    def __init__(self, registry_manager: AgentRegistryManager) -> None:
        self.registry_manager = registry_manager

    def can_use(self, name: str) -> bool:
        """بررسی می‌کند که ایجنت ثبت و فعال باشد."""
        return self.registry_manager.is_enabled(name)

    def available_agents(self) -> list[str]:
        """فهرست ایجنت‌های مجاز برای Manager را برمی‌گرداند."""
        return self.registry_manager.available()
