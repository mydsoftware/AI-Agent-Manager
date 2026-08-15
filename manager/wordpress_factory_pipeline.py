from __future__ import annotations

from dataclasses import dataclass

from agents.wordpress_factory_agent import WordPressFactoryAgent
from agents.wordpress_requirements_agent import WordPressRequirementsAgent
from agents.wordpress_theme_builder import WordPressThemeBuilder
from manager.wordpress_build_executor import WordPressBuildExecutor, WordPressBuildResult
from manager.wordpress_quality_loop import WordPressQualityLoop


@dataclass(frozen=True)
class WordPressFactoryResult:
    passed: bool
    plan: object
    requirements: object
    build: WordPressBuildResult
    quality_attempts: int
    findings: tuple[str, ...]


class WordPressFactoryPipeline:
    """Request → Requirements → Plan → Build → Theme Build → Quality/Repair → ZIP."""

    def __init__(self, max_quality_attempts: int = 3) -> None:
        self.requirements = WordPressRequirementsAgent()
        self.factory = WordPressFactoryAgent()
        self.builder = WordPressBuildExecutor()
        self.theme_builder = WordPressThemeBuilder()
        self.quality = WordPressQualityLoop(max_quality_attempts)

    def run(self, request: str, output_dir: str) -> WordPressFactoryResult:
        requirements = self.requirements.analyze(request)
        plan = self.factory.plan(request)
        build = self.builder.execute(plan, output_dir)
        self.theme_builder.build(requirements, build.root)
        quality = self.quality.run(build.root)
        return WordPressFactoryResult(
            quality.passed,
            plan,
            requirements,
            build,
            quality.attempts,
            quality.quality.findings,
        )
