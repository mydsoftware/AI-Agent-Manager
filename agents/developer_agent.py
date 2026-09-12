from __future__ import annotations

import json

from manager.llm_gateway import LLMGateway
from manager.model_router import ModelRouter
from manager.task import Task
from .base_agent import BaseAgent


class DeveloperAgent(BaseAgent):
    """ایجنت تخصصی توسعه نرم‌افزار برای اجرای وظایف کدنویسی."""

    name = "developer"

    def __init__(self, llm: LLMGateway | None = None, model_router: ModelRouter | None = None) -> None:
        self.llm = llm
        self.model_router = model_router or ModelRouter()

    def run(self, task: Task) -> str:
        """وظیفه توسعه را به برنامه استاندارد تبدیل می‌کند و در حالت LLM از مدل محلی کمک می‌گیرد."""
        try:
            command = json.loads(task.description)
        except (TypeError, json.JSONDecodeError):
            command = None

        if isinstance(command, dict):
            repository = command.get("repository")
            change = command.get("change")
            branch = command.get("branch")
            if repository and change and branch:
                plan = {
                    "type": "development_plan",
                    "repository": repository,
                    "branch": branch,
                    "change": change,
                    "base": command.get("base", "main"),
                    "workflow": command.get("workflow"),
                    "repair_change": command.get("repair_change"),
                    "pr": command.get("pr", {}),
                    "engineering_loop": True,
                }
                return json.dumps(plan, ensure_ascii=False)

            return json.dumps(
                {
                    "type": "development_plan",
                    "engineering_loop": False,
                    "message": "اطلاعات Repository، branch یا change برای اجرای خودکار کامل نیست.",
                },
                ensure_ascii=False,
            )

        if self.llm is None:
            return "وظیفه توسعه دریافت شد و برای تحلیل و پیاده‌سازی آماده است."

        model = self.model_router.resolve("developer")
        response = self.llm.complete(
            [
                {"role": "system", "content": "تو ایجنت توسعه نرم‌افزار AI-Agent-Manager هستی. پاسخ را عملی، دقیق و کوتاه بده و اگر نیاز به تغییر کد است، مراحل و فایل‌های درگیر را مشخص کن."},
                {"role": "user", "content": task.description},
            ],
            model,
            temperature=0.2,
        )
        return response.content
