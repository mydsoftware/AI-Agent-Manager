"""Helpers that inject retrieved project context into agent prompts."""

from __future__ import annotations

from .store import SharedMemory


class ContextManager:
    """Role-aware context retrieval before agent execution."""

    ROLE_HINTS = {
        "planner": "architecture requirement project_context decision",
        "developer": "code architecture decision requirement",
        "reviewer": "architecture decision code",
        "qa": "task_result code requirement",
        "game": "gdd asset_meta project_context",
        "database": "architecture code decision",
        "documentation": "requirement architecture task_result",
    }

    def __init__(self, memory: SharedMemory) -> None:
        self.memory = memory

    def for_agent(self, project_id: str, agent_role: str, query: str) -> str:
        hint = self.ROLE_HINTS.get(agent_role, "project_context")
        blended = f"{query} {hint}"
        return self.memory.retrieve_context(project_id, blended)

    def remember_task_result(self, project_id: str, title: str, result: str) -> None:
        self.memory.add(project_id, "task_result", title, result)

    def remember_decision(self, project_id: str, title: str, decision: str) -> None:
        self.memory.add(project_id, "decision", title, decision)

    def remember_code(self, project_id: str, path: str, code: str) -> None:
        self.memory.add(project_id, "code", path, code, {"path": path})
