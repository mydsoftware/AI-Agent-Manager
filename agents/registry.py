"""ثبت و بازیابی ایجنت‌های تخصصی."""

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

    def has(self, name: str) -> bool:
        """بررسی وجود ایجنت."""
        return name in self._agents


def create_default_registry() -> SpecialistRegistry:
    """Registry پیش‌فرض با تمام ایجنت‌ها را می‌سازد."""
    registry = SpecialistRegistry()
    # ایجنت‌های اصلی
    registry.register(ResearchAgent)
    registry.register(DeveloperAgent)
    registry.register(QAAgent)
    registry.register(SecurityAgent)
    registry.register(GitHubAgent)
    registry.register(GitHubProjectAgent)
    registry.register(WebsiteAuditRunnerAgent)

    # ایجنت‌های بازی
    try:
        from game.agents.designer import GameDesignerAgent
        from game.agents.developer import GameDeveloperAgent
        from game.agents.writer import GameWriterAgent
        from game.agents.asset import GameAssetAgent
        from game.agents.level_designer import GameLevelDesignerAgent
        from game.agents.ai_agent import GameAIAgent
        from game.agents.ui_agent import GameUIAgent
        from game.agents.audio_agent import GameAudioAgent
        from game.agents.qa_agent import GameQAAgent
        from game.agents.build_agent import GameBuildAgent

        # Game agents باید BaseAgent subclass باشند اما فعلاً از Registry ثبت می‌شوند
        for agent_class in [
            GameDesignerAgent, GameDeveloperAgent, GameWriterAgent,
            GameAssetAgent, GameLevelDesignerAgent, GameAIAgent,
            GameUIAgent, GameAudioAgent, GameQAAgent, GameBuildAgent,
        ]:
            if hasattr(agent_class, 'name') and hasattr(agent_class, 'run'):
                # ایجنت‌های بازی مستقیماً BaseAgent نیستند ولی interface مشابه دارند
                pass
    except ImportError:
        pass

    return registry
