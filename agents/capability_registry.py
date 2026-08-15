from __future__ import annotations

from collections import defaultdict

from .base_agent import BaseAgent
from .capability import AgentCapability


class CapabilityRegistry:
    """ثبت قابلیت‌های ایجنت‌ها و کشف ایجنت مناسب."""

    def __init__(self) -> None:
        self._capabilities: dict[str, list[AgentCapability]] = defaultdict(list)
        self._agents: dict[str, type[BaseAgent]] = {}

    def register(self, agent_class: type[BaseAgent], capabilities: list[AgentCapability]) -> None:
        self._agents[agent_class.name] = agent_class
        self._capabilities[agent_class.name] = list(capabilities)

    def find(self, requested: str) -> list[type[BaseAgent]]:
        return [
            self._agents[name]
            for name, capabilities in self._capabilities.items()
            if any(capability.matches(requested) for capability in capabilities)
        ]

    def capabilities(self, agent_name: str) -> list[AgentCapability]:
        return list(self._capabilities.get(agent_name, []))
