"""ایجنت نویسنده داستان بازی."""

from __future__ import annotations

import json

from ai_gateway import AIGateway, AIMessage, AIRequest
from manager.task import Task


class GameWriterAgent:
    """ایجنت تخصصی نوشتن داستان بازی."""

    name = "game-writer"

    def run(self, task: Task) -> str:
        """داستان، شخصیت‌ها و گفتگوهای بازی را می‌نویسد."""
        gateway = AIGateway()

        system_prompt = (
            "تو یک نویسنده داستان بازی حرفه‌ای فارسی هستی. "
            "داستان جذاب، شخصیت‌های به‌یادماندنی و گفتگوهای طبیعی بنویس."
        )

        response = gateway.complete(AIRequest(
            messages=[
                AIMessage(role="system", content=system_prompt),
                AIMessage(role="user", content=task.description),
            ]
        ))

        return json.dumps({
            "type": "game_story",
            "content": response.content,
            "ai_provider": response.provider,
            "ai_model": response.model,
        }, ensure_ascii=False, indent=2)
