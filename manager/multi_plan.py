from __future__ import annotations

from dataclasses import dataclass

from manager.intention import UserIntent
from manager.task import Task


@dataclass
class MultiAgentPlan:
    """برنامه اجرای چندایجنتی برای یک درخواست."""

    tasks: list[Task]


class MultiAgentPlanner:
    """درخواست‌های چندحوزه‌ای را به گراف وظایف تخصصی تبدیل می‌کند."""

    def plan(self, intent: UserIntent) -> MultiAgentPlan:
        """بر اساس نیت و کلیدواژه‌های فارسی/انگلیسی، زنجیره وظایف را می‌سازد."""
        text = intent.goal.lower()
        tasks: list[Task] = []

        def add(task_id: str, title: str, agent: str, keywords: tuple[str, ...]) -> None:
            if any(word in text for word in keywords):
                dependency = [tasks[-1].id] if tasks else []
                tasks.append(Task(task_id, title, intent.goal, agent, dependency))

        add("research-1", "تحلیل و تحقیق", "research", ("بررسی", "تحقیق", "تحلیل", "research"))
        add("developer-1", "طراحی و پیاده‌سازی", "developer", (
            "کدنویسی", "توسعه", "پیاده", "برنامه", "code", "بساز", "ساخت", "ایجاد", "create", "build", "website", "سایت"
        ))
        add("qa-1", "آزمون و کنترل کیفیت", "qa", ("تست", "آزمون", "بررسی نهایی", "test", "qa"))
        add("security-1", "بررسی امنیت", "security", ("امنیت", "security", "vulnerability", "آسیب‌پذیری"))
        add("github-1", "عملیات Repository", "github", ("github", "گیتهاب", "مخزن", "repository", "commit", "push", "pull request"))

        if not tasks:
            tasks.append(Task("task-1", "اجرای درخواست", intent.goal, intent.agent or "developer"))

        return MultiAgentPlan(tasks)
