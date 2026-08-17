from __future__ import annotations

import json

from ai_gateway import AIGateway, AIMessage, AIRequest
from manager.task import Task
from .base_agent import BaseAgent


class DeveloperAgent(BaseAgent):
    """ایجنت تخصصی توسعه نرم‌افزار برای اجرای وظایف کدنویسی."""

    name = "developer"

    def run(self, task: Task) -> str:
        """برنامه مهندسی را می‌سازد و از AI Gateway برای تحلیل کدنویسی استفاده می‌کند."""
        try:
            command = json.loads(task.description)
        except (TypeError, json.JSONDecodeError):
            command = {"change": task.description}

        if not isinstance(command, dict):
            return "فرمت وظیفه توسعه معتبر نیست."

        repository = command.get("repository")
        change = command.get("change")
        branch = command.get("branch")
        if not (repository and change and branch):
            return json.dumps({
                "type": "development_plan",
                "engineering_loop": False,
                "message": "اطلاعات Repository، branch یا change برای اجرای خودکار کامل نیست.",
            }, ensure_ascii=False)

        gateway = AIGateway()
        prompt = json.dumps(command, ensure_ascii=False)
        response = gateway.complete(AIRequest(messages=[
            AIMessage(role="system", content="تو ایجنت توسعه نرم‌افزار فارسی هستی. یک برنامه دقیق و قابل اجرای مهندسی برای تغییر خواسته‌شده تولید کن. اجرای مستقیم کد را بر عهده نگیر."),
            AIMessage(role="user", content=prompt),
        ]), preferred="omniroute")

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
            "ai_analysis": response.content,
            "ai_provider": response.provider,
            "ai_model": response.model,
        }
        return json.dumps(plan, ensure_ascii=False)
