from __future__ import annotations

import json

from ai_gateway import AIGateway, AIMessage, AIRequest
from manager.task import Task
from .base_agent import BaseAgent


class QAAgent(BaseAgent):
    """ایجنت تخصصی تضمین کیفیت برای تحلیل و اجرای سناریوهای آزمون."""

    name = "qa"

    def run(self, task: Task) -> str:
        """اطلاعات وظیفه آزمون را تحلیل و از AI Gateway برای طراحی QA استفاده می‌کند."""
        try:
            command = json.loads(task.description)
        except (TypeError, json.JSONDecodeError):
            return json.dumps({"type": "qa_plan", "valid": False, "message": "فرمت وظیفه آزمون معتبر نیست."}, ensure_ascii=False)

        if not isinstance(command, dict):
            return json.dumps({"type": "qa_plan", "valid": False, "message": "ساختار وظیفه آزمون معتبر نیست."}, ensure_ascii=False)

        repository = command.get("repository")
        branch = command.get("branch")
        test_command = command.get("test_command", "pytest")
        if not repository or not branch:
            return json.dumps({
                "type": "qa_plan", "valid": False, "engineering_loop": False,
                "message": "اطلاعات Repository یا branch برای اجرای آزمون کامل نیست.",
            }, ensure_ascii=False)

        gateway = AIGateway()
        response = gateway.complete(AIRequest(messages=[
            AIMessage(role="system", content="تو ایجنت QA فارسی هستی. برای تغییر نرم‌افزاری، سناریوهای تست، ریسک‌ها و معیار قبولی را مشخص کن."),
            AIMessage(role="user", content=json.dumps(command, ensure_ascii=False)),
        ]), preferred="freellmapi")

        return json.dumps({
            "type": "qa_plan", "valid": True, "engineering_loop": True,
            "repository": repository, "branch": branch, "test_command": test_command,
            "repair_change": command.get("repair_change"),
            "ai_analysis": response.content,
            "ai_provider": response.provider, "ai_model": response.model,
        }, ensure_ascii=False)
