from __future__ import annotations

from agents.registry import create_default_registry
from agents.registry_manager import AgentRegistryManager
from agents.registry_store import AgentRegistryStore
from manager.agent_governance import AgentGovernance
from manager.agent_team import AgentTeam
from manager.router import Router


class AgentTeamRuntime:
    """راه‌اندازی یک تیم Agent با وضعیت پایدار و Governance."""

    def __init__(self, registry_path: str = "data/agents.json") -> None:
        registry = create_default_registry()
        registry_manager = AgentRegistryManager(registry)
        store = AgentRegistryStore(registry_path)
        self.team = AgentTeam(registry_manager, store)
        self.governance = AgentGovernance(registry_manager)
        self.router = Router(registry, self.governance)
