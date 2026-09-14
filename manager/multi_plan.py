from __future__ import annotations

import json
import os
from dataclasses import dataclass

from manager.intent_router import IntentRouter
from manager.intention import UserIntent
from manager.task import Task


@dataclass
class MultiAgentPlan:
    """برنامه اجرای چندایجنتی برای یک درخواست."""
    tasks: list[Task]


class MultiAgentPlanner:
    """درخواست‌های چندحوزه‌ای را به وظایف تخصصی با ترتیب اجرایی تبدیل می‌کند."""

    def __init__(self, intent_router: IntentRouter | None = None) -> None:
        self.intent_router = intent_router or IntentRouter()

    def plan(self, intent: UserIntent) -> MultiAgentPlan:
        text = intent.goal.lower()
        route = self.intent_router.classify(intent.goal)
        tasks: list[Task] = []

        if route.intent == "vision":
            tasks.append(Task("developer-1", "تحلیل و پردازش تصویر", intent.goal, "developer", capability="vision"))
        elif route.intent == "research":
            tasks.append(Task("research-1", "تحلیل درخواست", intent.goal, "research", capability="general"))
        elif route.intent == "code":
            tasks.append(Task("developer-1", "پیاده‌سازی", intent.goal, "developer", capability="coder"))
        elif route.intent == "test":
            tasks.append(Task("qa-1", "آزمون نهایی", intent.goal, "qa", capability="coding"))
        elif route.intent == "plan":
            tasks.append(Task("developer-1", "طراحی راهکار", intent.goal, "developer", capability="general"))
        else:
            tasks.append(Task("developer-1", "اجرای درخواست", intent.goal, "developer", capability=route.capability))

        android_requested = any(word in text for word in ("android", "اندروید", "apk", "aab", "اپلیکیشن موبایل", "برنامه موبایل"))
        if android_requested:
            dependency = [tasks[-1].id]
            build_command = {
                "repository": os.getenv("AI_AGENT_MANAGER_REPOSITORY", "mydsoftware/AI-Agent-Manager"),
                "branch": os.getenv("AI_AGENT_MANAGER_BUILD_BRANCH", "feature/manager-core"),
                "workflows": ["android-build-automated.yml", "android-build.yml"],
                "timeout": int(os.getenv("AI_AGENT_MANAGER_BUILD_TIMEOUT", "900")),
            }
            tasks.append(Task("android-build-1", "بیلد و بسته‌بندی اندروید", json.dumps(build_command, ensure_ascii=False), "android-build", dependency, capability="android-build"))

        if any(word in text for word in ("تست", "آزمون", "بررسی نهایی", "test")) and not any(task.agent == "qa" for task in tasks):
            dependency = [tasks[-1].id]
            tasks.append(Task("qa-1", "آزمون نهایی", intent.goal, "qa", dependency, capability="coding"))

        # درخواست‌های واقعی GitHub توسط Developer → Engineering Loop انجام می‌شوند.
        # این Task فقط برای درخواست‌های مستقیم GitHub که مسیر توسعه ندارند لازم است.
        github_requested = any(word in text for word in ("github", "گیتهاب", "مخزن", "repository"))
        has_developer = any(task.agent == "developer" for task in tasks)
        if github_requested and not has_developer:
            dependency = [tasks[-1].id] if tasks else []
            tasks.append(Task("github-1", "عملیات GitHub", intent.goal, "github", dependency, capability="general"))

        return MultiAgentPlan(tasks)
