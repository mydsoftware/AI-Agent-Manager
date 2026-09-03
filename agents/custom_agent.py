from __future__ import annotations

import json

from ai_gateway import AIGateway, AIMessage, AIRequest
from manager.task import Task
from .base_agent import BaseAgent


class CustomAgent(BaseAgent):
    """ایجنت declarative ساخته‌شده توسط کاربر؛ بدون اجرای کد دلخواه."""

    config: dict[str, object] = {}

    def run(self, task: Task) -> str:
        prompt = str(self.config.get("system_prompt", "تو یک دستیار تخصصی هستی."))
        capabilities = str(self.config.get("capabilities", ""))
        user_request = task.description
        gateway = AIGateway()
        response = gateway.complete(
            AIRequest(messages=[
                AIMessage(role="system", content=f"{prompt}\nقابلیت‌های مجاز: {capabilities}"),
                AIMessage(role="user", content=user_request),
            ]),
            preferred="omniroute",
        )
        return json.dumps({
            "type": "custom_agent_result",
            "agent": self.name,
            "result": response.content,
            "provider": response.provider,
            "model": response.model,
        }, ensure_ascii=False)


def build_custom_agent(name: str, description: str, system_prompt: str, capabilities: list[str]):
    """کلاس ایجنت را فقط از تنظیمات داده‌ای می‌سازد و هیچ کد کاربر را اجرا نمی‌کند."""
    config = {
        "description": description,
        "system_prompt": system_prompt,
        "capabilities": ",".join(capabilities),
    }
    return type(
        f"Custom_{name.replace('-', '_').title()}",
        (CustomAgent,),
        {"name": name, "config": config},
    )
