"""ایجنت کنترل کیفیت بازی."""

from __future__ import annotations

import json

from ai_gateway import AIGateway, AIMessage, AIRequest
from manager.task import Task


class GameQAAgent:
    """ایجنت تخصصی تست و QA بازی."""

    name = "game-qa"

    CHECKLIST = [
        "launch", "main_menu", "start_game", "input_response",
        "movement", "collision", "combat", "enemy_ai",
        "level_transition", "save_load", "pause", "settings",
        "game_over", "victory",
    ]

    def run(self, task: Task) -> str:
        """تست جامع بازی را اجرا و گزارش تولید می‌کند."""
        gateway = AIGateway()

        system_prompt = (
            "تو یک مهندس QA بازی حرفه‌ای فارسی هستی. "
            "لیست تست بازی را بررسی و گزارش باگ‌ها و پیشنهادات را ارائه بده."
        )

        response = gateway.complete(AIRequest(
            messages=[
                AIMessage(role="system", content=system_prompt),
                AIMessage(role="user", content=task.description),
            ]
        ))

        return json.dumps({
            "type": "game_qa_report",
            "checklist": self.CHECKLIST,
            "analysis": response.content,
            "ai_provider": response.provider,
            "ai_model": response.model,
        }, ensure_ascii=False, indent=2)
