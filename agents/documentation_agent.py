"""Documentation specialist: README, API docs, architecture, changelog."""

from __future__ import annotations

from typing import Any

try:
    from agents.base_agent import BaseAgent
    from manager.task import Task
except Exception:

    class BaseAgent:  # type: ignore
        name = "base"

        def run(self, task: Any) -> str:
            raise NotImplementedError

    class Task:  # type: ignore
        def __init__(self, **kwargs: Any) -> None:
            self.__dict__.update(kwargs)


class DocumentationAgent(BaseAgent):
    name = "documentation"

    def run(self, task: Task) -> str:
        text = getattr(task, "description", None) or getattr(task, "goal", "") or str(task)
        kind = "readme"
        lowered = text.lower()
        if "openapi" in lowered or "swagger" in lowered:
            kind = "openapi"
        elif "api" in lowered:
            kind = "api"
        elif "architect" in lowered:
            kind = "architecture"
        elif "changelog" in lowered:
            kind = "changelog"
        elif "user" in lowered:
            kind = "user"
        elif "developer" in lowered:
            kind = "developer"
        return self.render(kind, text)

    def render(self, kind: str, spec: str) -> str:
        title = {
            "readme": "# Project README",
            "api": "# API Documentation",
            "architecture": "# Architecture",
            "changelog": "# Changelog",
            "user": "# User Guide",
            "developer": "# Developer Guide",
            "openapi": "openapi: 3.0.3\ninfo:\n  title: Generated API\n  version: 0.1.0\npaths: {}\n",
        }[kind]
        if kind == "openapi":
            return title
        return f"{title}\n\nGenerated from: {spec[:300]}\n\n## Overview\nThis document is kept in sync by DocumentationAgent.\n"
