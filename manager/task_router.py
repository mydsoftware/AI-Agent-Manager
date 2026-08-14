from __future__ import annotations

from dataclasses import dataclass

from agents.registry import SpecialistRegistry
from manager.agent_governance import AgentGovernance
from manager.task import Task


@dataclass(frozen=True)
class RoutingDecision:
    """تصمیم انتخاب ایجنت برای یک وظیفه."""

    agent: str
    دلیل: str


class IntelligentTaskRouter:
    """ایجنت مناسب را بر اساس نوع کار و متن وظیفه انتخاب می‌کند."""

    RULES = (
        ("github-project", ("github", "repository", "repo", "branch", "pull request", "pr", "commit", "فایل", "گیتهاب")),
        ("qa", ("test", "testing", "bug", "qa", "pytest", "تست", "خطا", "آزمون")),
        ("developer", ("code", "coding", "implement", "fix", "refactor", "develop", "کدنویسی", "پیاده", "اصلاح")),
        ("research", ("research", "analyze", "analysis", "investigate", "تحقیق", "بررسی", "تحلیل")),
    )

    def __init__(self, registry: SpecialistRegistry, governance: AgentGovernance | None = None) -> None:
        self.registry = registry
        self.governance = governance

    def select(self, task: Task) -> RoutingDecision:
        """بهترین ایجنت موجود را انتخاب می‌کند؛ نام صریح task اولویت دارد."""
        if task.agent in self.registry.names():
            self._authorize(task.agent)
            return RoutingDecision(task.agent, "ایجنت به‌صورت صریح در وظیفه تعیین شده است.")

        text = f"{task.description} {getattr(task, 'title', '')}".lower()
        for agent, keywords in self.RULES:
            if agent in self.registry.names() and any(keyword in text for keyword in keywords):
                self._authorize(agent)
                return RoutingDecision(agent, f"انتخاب بر اساس تشخیص نوع کار با کلیدواژه‌های مرتبط با «{agent}».")

        if "research" in self.registry.names():
            self._authorize("research")
            return RoutingDecision("research", "برای وظیفه بدون نشانه تخصصی، Research به‌عنوان مسیر پیش‌فرض انتخاب شد.")

        raise LookupError("هیچ ایجنت مناسبی برای این وظیفه ثبت نشده است.")

    def _authorize(self, agent: str) -> None:
        if self.governance is not None and not self.governance.can_use(agent):
            raise PermissionError(f"ایجنت «{agent}» غیرفعال یا غیرمجاز است.")
