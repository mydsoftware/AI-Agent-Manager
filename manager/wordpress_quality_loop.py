from __future__ import annotations

from dataclasses import dataclass

from agents.wordpress_quality_agent import WordPressQualityAgent, WordPressQualityResult
from agents.wordpress_repair_agent import WordPressRepairAgent


@dataclass(frozen=True)
class WordPressQualityLoopResult:
    passed: bool
    attempts: int
    quality: WordPressQualityResult


class WordPressQualityLoop:
    """Quality → Repair → Quality را برای خروجی WordPress اجرا می‌کند."""

    def __init__(self, max_attempts: int = 3) -> None:
        if max_attempts < 1:
            raise ValueError("max_attempts باید حداقل ۱ باشد.")
        self.max_attempts = max_attempts
        self.quality_agent = WordPressQualityAgent()
        self.repair_agent = WordPressRepairAgent()

    def run(self, root: str) -> WordPressQualityLoopResult:
        quality = self.quality_agent.validate(root)
        for attempt in range(1, self.max_attempts + 1):
            if quality.passed:
                return WordPressQualityLoopResult(True, attempt, quality)
            repair = self.repair_agent.repair(root, quality.findings)
            if not repair.changed:
                return WordPressQualityLoopResult(False, attempt, quality)
            quality = self.quality_agent.validate(root)
        return WordPressQualityLoopResult(quality.passed, self.max_attempts, quality)
