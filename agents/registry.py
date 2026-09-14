from __future__ import annotations

from typing import Dict, Type

from .base_agent import BaseAgent
from .android_build_agent import AndroidBuildAgent
from .developer_agent import DeveloperAgent
from .github_agent import GitHubAgent
from .github_project_agent import GitHubProjectAgent
from .qa_agent import QAAgent
from .research_agent import ResearchAgent


class SpecialistRegistry:
    """ثبت و بازیابی ایجنت‌های تخصصی."""

    def __init__(self) -> None:
        self._agents: Dict[str, Type[BaseAgent]] = {}
        self._instances: Dict[str, BaseAgent] = {}

    def register(self, agent_class: Type[BaseAgent]) -> None:
        self._agents[agent_class.name] = agent_class

    def register_instance(self, agent: BaseAgent) -> None:
        self._instances[agent.name] = agent

    def get(self, name: str) -> BaseAgent:
        if name in self._instances:
            return self._instances[name]
        if name not in self._agents:
            raise KeyError(f"ایجنت ثبت‌شده‌ای با نام «{name}» وجود ندارد.")
        return self._agents[name]()

    def names(self) -> list[str]:
        return sorted(set(self._agents) | set(self._instances))


def create_default_registry() -> SpecialistRegistry:
    """Registry پیش‌فرض پروژه را ایجاد می‌کند."""
    registry = SpecialistRegistry()
    registry.register(ResearchAgent)
    registry.register(DeveloperAgent)
    registry.register(QAAgent)
    registry.register(GitHubAgent)
    registry.register(GitHubProjectAgent)
    registry.register(AndroidBuildAgent)
    return registry
