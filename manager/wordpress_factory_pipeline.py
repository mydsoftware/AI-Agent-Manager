from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from agents.wordpress_factory_agent import WordPressFactoryAgent
from manager.wordpress_build_executor import WordPressBuildExecutor, WordPressBuildResult
from manager.wordpress_quality_loop import WordPressQualityLoop


@dataclass(frozen=True)
class WordPressFactoryResult:
    passed: bool
    plan: object
    build: WordPressBuildResult
    quality_attempts: int
    findings: tuple[str, ...]


class WordPressFactoryPipeline:
    """Request → Plan → Build → Quality/Repair → ZIP را یکپارچه می‌کند."""

    def __init__(self, max_quality_attempts: int = 3) -> None:
        self.factory = WordPressFactoryAgent()
        self.builder = WordPressBuildExecutor()
        self.quality = WordPressQualityLoop(max_quality_attempts)

    def run(self, request: str, output_dir: str) -> WordPressFactoryResult:
        plan = self.factory.plan(request)
        build = self.builder.execute(plan, output_dir)
        quality = self.quality.run(build.root)
        return WordPressFactoryResult(
            quality.passed,
            plan,
            build,
            quality.attempts,
            quality.quality.findings,
        )
