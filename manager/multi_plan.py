from __future__ import annotations

from dataclasses import dataclass

from manager.intent_router import IntentRouter
from manager.intention import UserIntent
from manager.task import Task


@dataclass
class MultiAgentPlan:
    """برنامه اجرای چندایجنتی برای یک درخواست."""

    tasks: list[Task]


class MultiAgentPlanner:
    """درخواست‌های چندحوزه‌ای را به چند وظیفه تخصصی تبدیل می‌کند."""

    def __init__(self, intent_router: IntentRouter | None = None) -> None:
        self.intent_router = intent_router or IntentRouter()

    def plan(self, intent: UserIntent) -> MultiAgentPlan:
        """بر اساس route اصلی، وظایف تخصصی و وابستگی‌های آن‌ها را می‌سازد."""
        text = intent.goal.lower()
        route = self.intent_router.classify(intent.goal)
        tasks: list[Task] = []

        # The primary route must win over broad keywords such as «بررسی».
        # In particular, a vision request must not accidentally become research.
        if route.intent == "vision":
            tasks.append(
                Task(
                    "developer-1",
                    "تحلیل و پردازش تصویر",
                    intent.goal,
                    "developer",
                    capability="vision",
                )
            )
        elif route.intent == "research":
            tasks.append(
                Task("research-1", "تحلیل درخواست", intent.goal, "research", capability="general")
            )
        elif route.intent == "code":
            tasks.append(
                Task("developer-1", "پیاده‌سازی", intent.goal, "developer", capability="coder")
            )
        elif route.intent == "test":
            tasks.append(Task("qa-1", "آزمون نهایی", intent.goal, "qa", capability="coding"))
        elif route.intent == "plan":
            tasks.append(
                Task("developer-1", "طراحی راهکار", intent.goal, "developer", capability="general")
            )

        # Add explicit secondary workflow stages after the primary task.
        if any(word in text for word in ("تست", "آزمون", "بررسی نهایی", "test")) and not any(
            task.agent == "qa" for task in tasks
        ):
            dependency = [tasks[-1].id] if tasks else []
            tasks.append(Task("qa-1", "آزمون نهایی", intent.goal, "qa", dependency, capability="coding"))

        if any(word in text for word in ("github", "گیتهاب", "مخزن", "repository")):
            dependency = [tasks[-1].id] if tasks else []
            tasks.append(Task("github-1", "عملیات GitHub", intent.goal, "github", dependency, capability="general"))

        if not tasks:
            tasks.append(Task("task-1", "اجرای درخواست", intent.goal, intent.agent or route.role, capability=route.capability))

        return MultiAgentPlan(tasks)
