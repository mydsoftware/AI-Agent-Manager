from __future__ import annotations

from agents.base_agent import BaseAgent
from agents.capability_registry import CapabilityRegistry


class AgentDiscovery:
    """انتخاب ایجنت بر اساس قابلیت موردنیاز."""

    def __init__(self, registry: CapabilityRegistry) -> None:
        self.registry = registry

    def discover(self, capability: str) -> type[BaseAgent] | None:
        matches = self.registry.find(capability)
        return matches[0] if matches else None
