from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable

from agents.test_generator_agent import GeneratedTest, TestGeneratorAgent


@dataclass(frozen=True)
class GeneratedTestSuite:
    tests: tuple[GeneratedTest, ...]
    test_command: str


class TestExecutionManager:
    """Test Generator را به اجرای واقعی QA متصل می‌کند."""

    def __init__(self, generator: TestGeneratorAgent | None = None) -> None:
        self.generator = generator or TestGeneratorAgent()

    def build_suite(self, request: str, diff: str | None = None, test_command: str = "pytest") -> GeneratedTestSuite:
        return GeneratedTestSuite(self.generator.generate(request, diff), test_command)

    def execute(self, suite: GeneratedTestSuite, runner: Callable[[str], str]) -> str:
        return runner(suite.test_command)

    @staticmethod
    def summary(suite: GeneratedTestSuite) -> dict[str, object]:
        return {
            "test_command": suite.test_command,
            "count": len(suite.tests),
            "tests": [
                {"name": item.name, "category": item.category, "scenario": item.scenario}
                for item in suite.tests
            ],
        }
