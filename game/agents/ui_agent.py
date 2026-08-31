"""ایجент رابط کاربری بازی."""

from __future__ import annotations

import json

from ai_gateway import AIGateway, AIMessage, AIRequest
from manager.task import Task


class GameUIAgent:
    """ایجنت تخصصی طراحی UI بازی."""

    name = "game-ui"

    def run(self, task: Task) -> str:
        """Menu, HUD, Inventory و صفحات UI بازی را طراحی می‌کند."""
        gateway = AIGateway()

        system_prompt = (
            "تو یک طراح UI بازی حرفه‌ای فارسی هستی. "
            "رابط کاربری جذاب و کاربردی برای بازی طراحی کن."
        )

        response = gateway.complete(AIRequest(
            messages=[
                AIMessage(role="system", content=system_prompt),
                AIMessage(role="user", content=task.description),
            ]
        ))

        return json.dumps({
            "type": "game_ui",
            "content": response.content,
            "ai_provider": response.provider,
            "ai_model": response.model,
        }, ensure_ascii=False, indent=2)
