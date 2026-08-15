from __future__ import annotations

from agents.registry_manager import AgentRegistryManager
from manager.agent_team import AgentTeam


class AgentTeamAPI:
    """رابط ساده مدیریتی برای کنترل تیم Agentها."""

    def __init__(self, team: AgentTeam, registry_manager: AgentRegistryManager) -> None:
        self.team = team
        self.registry_manager = registry_manager

    def list_agents(self) -> list[dict[str, object]]:
        """فهرست Agentها و وضعیت فعال بودن آن‌ها را برمی‌گرداند."""
        return [
            {
                "name": name,
                "enabled": self.registry_manager.is_enabled(name),
            }
            for name in sorted(self.registry_manager._records)
        ]

    def enable(self, name: str) -> dict[str, object]:
        """یک Agent را فعال می‌کند."""
        self.team.enable(name)
        return {"name": name, "enabled": True}

    def disable(self, name: str) -> dict[str, object]:
        """یک Agent را غیرفعال می‌کند."""
        self.team.disable(name)
        return {"name": name, "enabled": False}
