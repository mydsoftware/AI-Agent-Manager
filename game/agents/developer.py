"""ایجنت توسعه بازی."""

from __future__ import annotations

import json

from ai_gateway import AIGateway, AIMessage, AIRequest
from manager.task import Task


class GameDeveloperAgent:
    """ایجنت تخصصی توسعه بازی - پیاده‌سازی مکانیک‌ها و کد."""

    name = "game-developer"

    def run(self, task: Task) -> str:
        """کد بازی را بر اساس طراحی و مکانیک‌ها پیاده‌سازی می‌کند."""
        gateway = AIGateway()

        system_prompt = (
            "تو یک توسعه‌دهنده بازی حرفه‌ای فارسی هستی. "
            "بر اساس طراحی بازی، کد قابل اجرا تولید کن. "
            "از Godot GDScript یا Phaser JavaScript استفاده کن."
        )

        response = gateway.complete(AIRequest(
            messages=[
                AIMessage(role="system", content=system_prompt),
                AIMessage(role="user", content=task.description),
            ]
        ))

        return json.dumps({
            "type": "game_code",
            "analysis": response.content,
            "ai_provider": response.provider,
            "ai_model": response.model,
        }, ensure_ascii=False, indent=2)
