from __future__ import annotations

import json
import os

from manager.llm_gateway import LLMGateway
from manager.model_router import ModelRouter
from manager.task import Task
from .base_agent import BaseAgent


class DeveloperAgent(BaseAgent):
    """ایجنت توسعه؛ درخواست طبیعی را به برنامه اجرایی ساختاریافته تبدیل می‌کند."""

    name = "developer"

    SYSTEM_PROMPT = """تو Developer Agent پروژه AI-Agent-Manager هستی.
درخواست طبیعی کاربر را به برنامه اجرایی قابل‌اجرا تبدیل کن.
اگر درخواست ساخت یا تغییر نرم‌افزار است، فقط JSON معتبر برگردان و هیچ Markdown اضافه نکن.
ساختار JSON:
{"type":"development_plan","engineering_loop":true,"repository":"owner/repo","base":"main","branch":"feature/ai-short-name","workflow":"ci.yml","changes":[{"path":"relative/path","content":"complete file content","message":"commit message"}],"repair_changes":[],"pr":{"title":"...","body":"...","draft":true}}
هر فایل باید محتوای کامل داشته باشد. از اطلاعات Repository در خروجی preflight برای حفظ ساختار فعلی استفاده کن.
هیچ Secret یا token داخل خروجی قرار نده.
اگر درخواست فقط تحلیل است، engineering_loop=false برگردان.
"""

    def __init__(self, llm: LLMGateway | None = None, model_router: ModelRouter | None = None) -> None:
        self.llm = llm
        self.model_router = model_router or ModelRouter()

    def run(self, task: Task) -> str:
        try:
            command = json.loads(task.description)
        except (TypeError, json.JSONDecodeError):
            command = None

        if isinstance(command, dict) and command.get("repository") and command.get("branch"):
            changes = command.get("changes")
            if not changes and command.get("change"):
                changes = [{
                    "path": "ENGINEERING_REQUEST.md",
                    "content": str(command["change"]) + "\n",
                    "message": "chore: record engineering request",
                }]
            if changes:
                return json.dumps({
                    "type": "development_plan", "engineering_loop": True,
                    "repository": command["repository"], "base": command.get("base", "main"),
                    "branch": command["branch"], "workflow": command.get("workflow", "ci.yml"),
                    "changes": changes, "repair_changes": command.get("repair_changes", []),
                    "pr": command.get("pr", {}),
                }, ensure_ascii=False)

        if self.llm is None:
            return json.dumps({"type":"development_plan","engineering_loop":False,"message":"LLM برای تولید برنامه اجرایی در دسترس نیست."}, ensure_ascii=False)

        model = self.model_router.resolve("developer", capability=task.capability)
        repository = os.getenv("AI_AGENT_MANAGER_REPOSITORY", "mydsoftware/AI-Agent-Manager")
        branch = os.getenv("AI_AGENT_MANAGER_BUILD_BRANCH", "feature/manager-core")
        user_prompt = f"مخزن هدف: {repository}\nشاخه کاری پیش‌فرض: {branch}\n\nدرخواست کاربر:\n{task.description}"
        response = self.llm.complete(
            [{"role":"system","content":self.SYSTEM_PROMPT},{"role":"user","content":user_prompt}],
            model, temperature=0.1,
        )
        raw = response.content.strip()
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict) and parsed.get("type") == "development_plan":
                parsed.setdefault("repository", repository)
                parsed.setdefault("base", "main")
                parsed.setdefault("branch", branch)
                return json.dumps(parsed, ensure_ascii=False)
        except json.JSONDecodeError:
            if task.capability in {"vision", "coder"}:
                return raw
        return json.dumps({"type":"development_plan","engineering_loop":False,"message":"مدل نتوانست برنامه اجرایی JSON تولید کند.","analysis":raw}, ensure_ascii=False)
