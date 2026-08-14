from __future__ import annotations

import json

from manager.task import Task
from .base_agent import BaseAgent


class DeveloperAgent(BaseAgent):
    """ایجنت تخصصی توسعه نرم‌افزار برای اجرای وظایف کدنویسی."""

    name = "developer"

    def run(self, task: Task) -> str:
        """وظیفه توسعه را به یک برنامه استاندارد برای اجرای مهندسی تبدیل می‌کند."""
        try:
            command = json.loads(task.description)
        except (TypeError, json.JSONDecodeError):
            return "وظیفه توسعه دریافت شد و برای تحلیل و پیاده‌سازی آماده است."

        if not isinstance(command, dict):
            return "فرمت وظیفه توسعه معتبر نیست."

        repository = command.get("repository")
        change = command.get("change")
        branch = command.get("branch")

        if repository and change and branch:
            return json.dumps(
                {
                    "type": "development_plan",
                    "repository": repository,
                    "branch": branch,
                    "change": change,
                    "engineering_loop": True,
                },
                ensure_ascii=False,
            )

        return json.dumps(
            {
                "type": "development_plan",
                "engineering_loop": False,
                "message": "اطلاعات Repository، branch یا change برای اجرای خودکار کامل نیست.",
            },
            ensure_ascii=False,
        )
