from __future__ import annotations

from dataclasses import dataclass

from .base_agent import BaseAgent
from .capability import AgentCapability
from .capability_registry import CapabilityRegistry


@dataclass(frozen=True)
class AgentSpecification:
    """مشخصات لازم برای ساخت یک Agent تخصصی."""

    name: str
    capability: AgentCapability


class AgentFactory:
    """ساخت و ثبت Agentهای تخصصی در Runtime."""

    def __init__(self, registry: CapabilityRegistry) -> None:
        self.registry = registry

    def create(self, specification: AgentSpecification) -> type[BaseAgent]:
        """یک Agent پایه قابل اجرا می‌سازد و در Registry ثبت می‌کند."""

        capability = specification.capability

        class GeneratedAgent(BaseAgent):
            name = specification.name

            def run(self, task) -> str:
                return f"Agent '{self.name}' آماده اجرای task است: {task.title}"

        GeneratedAgent.__name__ = "GeneratedAgent"
        self.registry.register(GeneratedAgent, [capability])
        return GeneratedAgent
