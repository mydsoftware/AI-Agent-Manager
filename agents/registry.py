from __future__ import annotations

from typing import Dict, Type

from .base_agent import BaseAgent
from .developer_agent import DeveloperAgent
from .github_agent import GitHubAgent
from .github_project_agent import GitHubProjectAgent
from .qa_agent import QAAgent
from .research_agent import ResearchAgent


class SpecialistRegistry:
    """ثبت و بازیابی ایجنت‌های تخصصی."""

    def __init__(self) -> None:
        self._agents: Dict[str, Type[BaseAgent]] = {}

    def register(self, agent_class: Type[BaseAgent]) -> None:
        """یک ایجنت تخصصی را با نام آن ثبت می‌کند."""
        self._agents[agent_class.name] = agent_class

    def get(self, name: str) -> BaseAgent:
        """یک نمونه از ایجنت موردنظر را برمی‌گرداند."""
        if name not in self._agents:
            raise KeyError(f"ایجنت ثبت‌شده‌ای با نام «{name}» وجود ندارد.")
        return self._agents[name]()

    def names(self) -> list[str]:
        """نام تمام ایجنت‌های ثبت‌شده را برمی‌گرداند."""
        return sorted(self._agents)


def create_default_registry() -> SpecialistRegistry:
    """Registry پیش‌فرض پروژه را ایجاد می‌کند."""
    registry = SpecialistRegistry()
    registry.register(ResearchAgent)
    registry.register(DeveloperAgent)
    registry.register(QAAgent)
    registry.register(GitHubAgent)
    registry.register(GitHubProjectAgent)
    return registry
