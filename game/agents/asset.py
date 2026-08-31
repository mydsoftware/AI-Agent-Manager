"""ایجنت مدیریت Assetهای بازی."""

from __future__ import annotations

import json
from typing import Any

from manager.task import Task


class GameAssetAgent:
    """ایجنت تخصصی مدیریت Assetهای بازی."""

    name = "game-asset"

    CATEGORIES = [
        "characters", "enemies", "bosses", "environment",
        "backgrounds", "tiles", "objects", "weapons",
        "items", "ui", "icons",
    ]

    def run(self, task: Task) -> str:
        """Plan Assetهای مورد نیاز بازی را تولید می‌کند."""
        try:
            command = json.loads(task.description)
        except (json.JSONDecodeError, TypeError):
            command = {"description": task.description}

        assets: list[dict[str, Any]] = []
        for category in self.CATEGORIES:
            category_assets = command.get("assets", {}).get(category, [])
            for asset in category_assets:
                assets.append({
                    "id": asset.get("id", f"{category}_{len(assets)}"),
                    "type": category,
                    "path": f"assets/{category}/{asset.get('filename', 'asset.png')}",
                    "width": asset.get("width", 512),
                    "height": asset.get("height", 512),
                    "transparent": asset.get("transparent", False),
                    "prompt": asset.get("prompt", ""),
                    "style": asset.get("style", "pixel_art"),
                })

        manifest = {
            "version": "1.0",
            "total_assets": len(assets),
            "categories": {cat: len([a for a in assets if a["type"] == cat]) for cat in self.CATEGORIES},
            "assets": assets,
        }

        return json.dumps({
            "type": "asset_plan",
            "manifest": manifest,
        }, ensure_ascii=False, indent=2)
