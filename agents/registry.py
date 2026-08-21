from __future__ import annotations

from typing import Dict, Type

from .base_agent import BaseAgent
from .developer_agent import DeveloperAgent
from .github_agent import GitHubAgent
from .github_project_agent import GitHubProjectAgent
from .qa_agent import QAAgent
from .research_agent import ResearchAgent
from .security_agent import SecurityAgent
from .website_audit_runner import WebsiteAuditRunnerAgent


class SpecialistRegistry:
    """ثبت و بازیابی ایجنت‌های تخصصی."""

    def __init__(self) -> None:
        self._agents: Dict[str, Type[BaseAgent]] = {}

    def register(self, agent_class: Type[BaseAgent]) -> None:
        self._agents[agent_class.name] = agent_class

    def get(self, name: str) -> BaseAgent:
        if name not in self._agents:
            raise KeyError(f"ایجنت ثبت‌شده‌ای با نام «{name}» وجود ندارد.")
        return self._agents[name]()

    def names(self) -> list[str]:
        return sorted(self._agents)


def create_default_registry() -> SpecialistRegistry:
    registry = SpecialistRegistry()
    registry.register(ResearchAgent)
    registry.register(DeveloperAgent)
    registry.register(QAAgent)
    registry.register(SecurityAgent)
    registry.register(GitHubAgent)
    registry.register(GitHubProjectAgent)
    registry.register(WebsiteAuditRunnerAgent)
    return registry
