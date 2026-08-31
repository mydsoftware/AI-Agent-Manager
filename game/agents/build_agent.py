"""ایجنت Build بازی."""

from __future__ import annotations

import json
import os
import subprocess
from typing import Any

from manager.task import Task


class GameBuildAgent:
    """ایجنت تخصصی Build و Package بازی."""

    name = "game-build"

    def run(self, task: Task) -> str:
        """Build بازی را برای پلتفرم‌های مختلف اجرا می‌کند."""
        try:
            command = json.loads(task.description)
        except (json.JSONDecodeError, TypeError):
            command = {"platform": "web"}

        platform = command.get("platform", "web")
        workspace = command.get("workspace", os.getcwd())

        build_results: dict[str, Any] = {"platform": platform, "outputs": []}

        if platform == "web":
            result = self._build_web(workspace, command)
            build_results["outputs"].append(result)
        elif platform == "android":
            result = self._build_android(workspace, command)
            build_results["outputs"].append(result)
        elif platform == "windows":
            result = self._build_windows(workspace, command)
            build_results["outputs"].append(result)
        else:
            build_results["outputs"].append({
                "status": "unsupported",
                "message": f"پلتفرم «{platform}» هنوز پشتیبانی نمی‌شود.",
            })

        return json.dumps({
            "type": "build_result",
            "build": build_results,
        }, ensure_ascii=False, indent=2)

    def _build_web(self, workspace: str, command: dict) -> dict:
        """Build وب."""
        output_dir = os.path.join(workspace, "dist", "web")
        os.makedirs(output_dir, exist_ok=True)
        return {"status": "prepared", "output": output_dir, "platform": "web"}

    def _build_android(self, workspace: str, command: dict) -> dict:
        """Build اندروید."""
        output_dir = os.path.join(workspace, "dist", "android")
        os.makedirs(output_dir, exist_ok=True)
        return {"status": "prepared", "output": output_dir, "platform": "android"}

    def _build_windows(self, workspace: str, command: dict) -> dict:
        """Build ویندوز."""
        output_dir = os.path.join(workspace, "dist", "windows")
        os.makedirs(output_dir, exist_ok=True)
        return {"status": "prepared", "output": output_dir, "platform": "windows"}
