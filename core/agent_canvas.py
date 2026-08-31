"""Agent Canvas — OpenHands-style developer control center.

Self-hosted control center for managing coding agents, automations,
and conversations. Inspired by OpenHands Agent Canvas.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable


class CanvasStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    ERROR = "error"


@dataclass
class Conversation:
    """A conversation thread with an agent."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:10])
    title: str = ""
    agent_type: str = "default"
    messages: list[dict] = field(default_factory=list)
    status: CanvasStatus = CanvasStatus.IDLE
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    def add_message(self, role: str, content: str, **kwargs: Any) -> dict:
        msg = {
            "role": role,
            "content": content,
            "timestamp": time.time(),
            **kwargs,
        }
        self.messages.append(msg)
        self.updated_at = time.time()
        return msg

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "agent_type": self.agent_type,
            "message_count": len(self.messages),
            "status": self.status.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


@dataclass
class Automation:
    """An automated workflow triggered by events or schedules."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:10])
    name: str = ""
    trigger: str = ""  # webhook, schedule, event
    agent_type: str = ""
    task: str = ""
    enabled: bool = True
    last_run: float | None = None
    run_count: int = 0

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "trigger": self.trigger,
            "agent_type": self.agent_type,
            "task": self.task[:100],
            "enabled": self.enabled,
            "last_run": self.last_run,
            "run_count": self.run_count,
        }


class AgentCanvas:
    """Developer control center for managing agents.

    Features:
    - Conversation threads with agents
    - Automation workflows
    - Task tracking
    - Agent backend management
    """

    def __init__(self) -> None:
        self._conversations: dict[str, Conversation] = {}
        self._automations: dict[str, Automation] = {}
        self._backends: dict[str, dict] = {}
        self._tasks: list[dict] = []

    # ── Conversations ──────────────────────────────────────

    def create_conversation(
        self, title: str = "", agent_type: str = "default"
    ) -> Conversation:
        conv = Conversation(title=title, agent_type=agent_type)
        self._conversations[conv.id] = conv
        return conv

    def get_conversation(self, conv_id: str) -> Conversation | None:
        return self._conversations.get(conv_id)

    def list_conversations(self, limit: int = 20) -> list[dict]:
        convs = sorted(self._conversations.values(),
                      key=lambda c: c.updated_at, reverse=True)
        return [c.to_dict() for c in convs[:limit]]

    def send_message(self, conv_id: str, content: str) -> dict | None:
        conv = self._conversations.get(conv_id)
        if not conv:
            return None
        conv.add_message("user", content)
        # In production, this triggers the agent
        conv.add_message("assistant", "[Agent response would go here]")
        return conv.messages[-1]

    # ── Automations ────────────────────────────────────────

    def create_automation(self, **kwargs: Any) -> Automation:
        auto = Automation(**kwargs)
        self._automations[auto.id] = auto
        return auto

    def list_automations(self) -> list[dict]:
        return [a.to_dict() for a in self._automations.values()]

    def trigger_automation(self, auto_id: str) -> dict:
        auto = self._automations.get(auto_id)
        if not auto:
            return {"error": "Automation not found"}
        if not auto.enabled:
            return {"error": "Automation disabled"}

        auto.last_run = time.time()
        auto.run_count += 1
        return {"status": "triggered", "automation": auto.name}

    # ── Backends ───────────────────────────────────────────

    def register_backend(self, name: str, config: dict) -> None:
        self._backends[name] = {
            "name": name,
            "status": "ready",
            **config,
        }

    def list_backends(self) -> list[dict]:
        return list(self._backends.values())

    # ── Tasks ──────────────────────────────────────────────

    def add_task(self, description: str, agent_type: str = "default") -> dict:
        task = {
            "id": str(uuid.uuid4())[:8],
            "description": description,
            "agent_type": agent_type,
            "status": "pending",
            "created_at": time.time(),
        }
        self._tasks.append(task)
        return task

    def list_tasks(self, status: str | None = None) -> list[dict]:
        if status:
            return [t for t in self._tasks if t["status"] == status]
        return self._tasks

    # ── Summary ────────────────────────────────────────────

    def summary(self) -> dict:
        return {
            "conversations": len(self._conversations),
            "automations": len(self._automations),
            "backends": len(self._backends),
            "tasks": len(self._tasks),
            "pending_tasks": len([t for t in self._tasks if t["status"] == "pending"]),
        }
