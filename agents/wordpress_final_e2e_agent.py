from __future__ import annotations

from dataclasses import dataclass

from manager.wordpress_factory_pipeline import WordPressFactoryPipeline, WordPressFactoryResult


@dataclass(frozen=True)
class WordPressFinalE2EResult:
    passed: bool
    stages: tuple[str, ...]
    findings: tuple[str, ...]
    result: WordPressFactoryResult


class WordPressFinalE2EAgent:
    """Single final gate for the complete WordPress Factory lifecycle."""

    def run(self, request: str, output_dir: str) -> WordPressFinalE2EResult:
        result = WordPressFactoryPipeline().run(request, output_dir)
        stages = (
            "requirements", "build", "quality", "package", "smoke", "ui",
            "browser", "delivery", "installer",
        )
        return WordPressFinalE2EResult(result.passed, stages, result.findings, result)
