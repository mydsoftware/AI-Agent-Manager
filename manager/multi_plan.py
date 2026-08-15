from __future__ import annotations

from dataclasses import dataclass

from manager.intention import UserIntent
from manager.task import Task


@dataclass
class MultiAgentPlan:
    """برنامه اجرای چندایجنتی برای یک درخواست."""

    tasks: list[Task]


class MultiAgentPlanner:
    """درخواست‌های چندحوزه‌ای را به چند وظیفه تخصصی تبدیل می‌کند."""

    def plan(self, intent: UserIntent) -> MultiAgentPlan:
        """بر اساس حوزه‌های تشخیص‌داده‌شده، زنجیره‌ای از وظایف می‌سازد."""
        text = intent.goal.lower()
        tasks: list[Task] = []

        if any(word in text for word in ("بررسی", "تحقیق", "تحلیل", "research")):
            tasks.append(Task("research-1", "تحلیل درخواست", intent.goal, "research"))

        if any(word in text for word in ("کدنویسی", "توسعه", "پیاده", "برنامه", "code")):
            dependency = [tasks[-1].id] if tasks else []
            tasks.append(Task("developer-1", "پیاده‌سازی", intent.goal, "developer", dependency))

        if any(word in text for word in ("تست", "آزمون", "بررسی نهایی", "test")):
            dependency = [tasks[-1].id] if tasks else []
            tasks.append(Task("qa-1", "آزمون نهایی", intent.goal, "qa", dependency))

        if any(word in text for word in ("github", "گیتهاب", "مخزن", "repository")):
            dependency = [tasks[-1].id] if tasks else []
            tasks.append(Task("github-1", "عملیات GitHub", intent.goal, "github", dependency))

        if not tasks:
            tasks.append(Task("task-1", "اجرای درخواست", intent.goal, intent.agent or "developer"))

        return MultiAgentPlan(tasks)
