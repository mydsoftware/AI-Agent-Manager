from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from agents.github_project_agent import GitHubProjectAgent
from manager.task import Task


@dataclass
class EngineeringStep:
    """نتیجه یک گام از چرخه مهندسی."""

    name: str
    success: bool
    result: str | None = None
    error: str | None = None


@dataclass
class EngineeringLoopResult:
    """نتیجه نهایی چرخه مهندسی خودکار."""

    success: bool
    steps: list[EngineeringStep] = field(default_factory=list)
    attempts: int = 0


class AutonomousEngineeringLoop:
    """چرخه امن Branch → تغییر → بررسی CI → اصلاح → PR را مدیریت می‌کند.

    این چرخه به‌صورت پیش‌فرض PR را Merge نمی‌کند و برای اصلاح، یک تابع
    repair دریافت می‌کند تا تصمیم اصلاح از Agent تخصصی گرفته شود.
    """

    def __init__(self, project_agent: GitHubProjectAgent | None = None, max_attempts: int = 3) -> None:
        if max_attempts < 1:
            raise ValueError("max_attempts باید حداقل ۱ باشد.")
        self.project_agent = project_agent or GitHubProjectAgent()
        self.max_attempts = max_attempts

    def _run(self, task_id: str, operation: str, repository: str, **kwargs) -> str:
        command = {"operation": operation, "repository": repository, **kwargs}
        return self.project_agent.run(Task(
            id=task_id,
            title=f"چرخه مهندسی: {operation}",
            description=__import__("json").dumps(command, ensure_ascii=False),
            agent="github-project",
        ))

    def execute(
        self,
        repository: str,
        base: str,
        branch: str,
        repair: Callable[[str], bool] | None = None,
        pr_title: str = "تغییرات تولیدشده توسط Manager",
        pr_body: str = "این Pull Request توسط چرخه مهندسی خودکار Manager ایجاد شده است.",
    ) -> EngineeringLoopResult:
        """چرخه را اجرا می‌کند و تا سقف max_attempts برای اصلاح تلاش می‌کند."""
        result = EngineeringLoopResult(success=False)
        try:
            branch_result = self._run("loop:branch", "create_branch", repository, branch=branch, base=base)
            result.steps.append(EngineeringStep("ایجاد شاخه", True, branch_result))
        except Exception as error:
            result.steps.append(EngineeringStep("ایجاد شاخه", False, error=str(error)))
            return result

        for attempt in range(1, self.max_attempts + 1):
            result.attempts = attempt
            try:
                status = self._run("loop:ci", "workflow_status", repository, branch=branch)
                result.steps.append(EngineeringStep(f"بررسی CI تلاش {attempt}", True, status))
                if '"failure"' not in status.lower() and '"cancelled"' not in status.lower() and '"timed_out"' not in status.lower():
                    pr = self._run("loop:pr", "create_pr", repository, head=branch, base=base, title=pr_title, body=pr_body, draft=True)
                    result.steps.append(EngineeringStep("ایجاد Pull Request", True, pr))
                    result.success = True
                    return result
            except Exception as error:
                result.steps.append(EngineeringStep(f"بررسی چرخه تلاش {attempt}", False, error=str(error)))
                if repair is None or not repair(str(error)):
                    return result
                result.steps.append(EngineeringStep(f"اصلاح تلاش {attempt}", True))

        return result
