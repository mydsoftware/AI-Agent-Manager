"""ایجنت طراحی بازی."""

from __future__ import annotations

import json

from ai_gateway import AIGateway, AIMessage, AIRequest
from manager.task import Task


class GameDesignerAgent:
    """ایجنت تخصصی طراحی بازی - تولید GDD و مکانیک‌ها."""

    name = "game-designer"

    def run(self, task: Task) -> str:
        """طراحی بازی را از درخواست کاربر تحلیل و GDD تولید می‌کند."""
        gateway = AIGateway()

        system_prompt = (
            "تو یک طراح بازی حرفه‌ای فارسی هستی. "
            "درخواست کاربر را تحلیل کن و یک Game Design Document کامل تولید کن. "
            "خروجی باید JSON معتبر باشد."
        )

        response = gateway.complete(AIRequest(
            messages=[
                AIMessage(role="system", content=system_prompt),
                AIMessage(role="user", content=task.description),
            ]
        ))

        try:
            design = json.loads(response.content)
        except (json.JSONDecodeError, TypeError):
            design = {
                "game_name": "بازی جدید",
                "genre": "نامشخص",
                "analysis": response.content,
                "core_mechanics": [],
                "gameplay_loop": "",
                "target_platform": "multi",
            }

        return json.dumps({
            "type": "game_design",
            "design": design,
            "ai_provider": response.provider,
            "ai_model": response.model,
        }, ensure_ascii=False, indent=2)
