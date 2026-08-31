"""ایجنت هوش مصنوعی بازی."""

from __future__ import annotations

import json

from ai_gateway import AIGateway, AIMessage, AIRequest
from manager.task import Task


class GameAIAgent:
    """ایجنت تخصصی هوش مصنوعی دشمنان و NPCها."""

    name = "game-ai"

    def run(self, task: Task) -> str:
        """سیستم‌های AI بازی (FSM, Behavior Tree) را طراحی و پیاده‌سازی می‌کند."""
        gateway = AIGateway()

        system_prompt = (
            "تو یک متخصص AI بازی فارسی هستی. "
            "FSM یا Behavior Tree برای دشمنان و NPCها طراحی کن."
        )

        response = gateway.complete(AIRequest(
            messages=[
                AIMessage(role="system", content=system_prompt),
                AIMessage(role="user", content=task.description),
            ]
        ))

        return json.dumps({
            "type": "game_ai",
            "content": response.content,
            "ai_provider": response.provider,
            "ai_model": response.model,
        }, ensure_ascii=False, indent=2)
