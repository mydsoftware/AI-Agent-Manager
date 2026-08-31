"""ایجنت طراحی سطوح بازی."""

from __future__ import annotations

import json

from ai_gateway import AIGateway, AIMessage, AIRequest
from manager.task import Task


class GameLevelDesignerAgent:
    """ایجنت تخصصی طراحی Layout سطوح."""

    name = "game-level-designer"

    def run(self, task: Task) -> str:
        """Layout و محتوای سطوح بازی را طراحی می‌کند."""
        gateway = AIGateway()

        system_prompt = (
            "تو یک طراح سطوح بازی حرفه‌ای فارسی هستی. "
            "Layout، دشمنان، آیتم‌ها، چک‌پوینت‌ها و مسیر بازیکن را طراحی کن."
        )

        response = gateway.complete(AIRequest(
            messages=[
                AIMessage(role="system", content=system_prompt),
                AIMessage(role="user", content=task.description),
            ]
        ))

        return json.dumps({
            "type": "level_design",
            "content": response.content,
            "ai_provider": response.provider,
            "ai_model": response.model,
        }, ensure_ascii=False, indent=2)
