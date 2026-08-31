"""ایجنت صدا و موسیقی بازی."""

from __future__ import annotations

import json

from manager.task import Task


class GameAudioAgent:
    """ایجنت تخصصی موسیقی، SFX و صداهای بازی."""

    name = "game-audio"

    def run(self, task: Task) -> str:
        """Plan صداهای مورد نیاز بازی را تولید می‌کند."""
        try:
            command = json.loads(task.description)
        except (json.JSONDecodeError, TypeError):
            command = {"description": task.description}

        audio_plan = {
            "music": command.get("music", []),
            "sfx": command.get("sfx", []),
            "ambience": command.get("ambience", []),
            "ui_sounds": command.get("ui_sounds", []),
            "structure": {
                "music": "assets/audio/music/",
                "sfx": "assets/audio/sfx/",
                "ambience": "assets/audio/ambience/",
                "ui": "assets/audio/ui/",
            },
        }

        return json.dumps({
            "type": "audio_plan",
            "plan": audio_plan,
        }, ensure_ascii=False, indent=2)
