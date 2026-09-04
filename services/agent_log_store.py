"""ذخیره‌سازی پایدار لاگ اجرای Agentها."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


class AgentLogStore:
    """رویدادهای قابل مشاهده اجرای Agent را در SQLite نگه می‌دارد."""

    def __init__(self, database_path: str = "data/platform.db") -> None:
        self.database_path = database_path
        Path(database_path).parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(database_path) as db:
            db.execute(
                """CREATE TABLE IF NOT EXISTS agent_logs (
                    id TEXT PRIMARY KEY,
                    project_id TEXT,
                    workflow_id TEXT,
                    task_id TEXT,
                    agent TEXT NOT NULL,
                    level TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    message TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )"""
            )
            db.execute(
                "CREATE INDEX IF NOT EXISTS idx_agent_logs_project ON agent_logs(project_id, created_at)"
            )
            db.execute(
                "CREATE INDEX IF NOT EXISTS idx_agent_logs_task ON agent_logs(task_id, created_at)"
            )

    def add(
        self,
        agent: str,
        event_type: str,
        message: str,
        *,
        project_id: str | None = None,
        workflow_id: str | None = None,
        task_id: str | None = None,
        level: str = "info",
        metadata: dict | None = None,
    ) -> dict[str, object]:
        import json

        agent = str(agent).strip()
        event_type = str(event_type).strip()
        message = str(message).strip()
        level = str(level).strip().lower()
        if not agent or not event_type or not message:
            raise ValueError("agent، event_type و message الزامی هستند.")
        if level not in {"debug", "info", "warning", "error"}:
            raise ValueError("level نامعتبر است.")
        item = {
            "id": str(uuid4()),
            "project_id": project_id,
            "workflow_id": workflow_id,
            "task_id": task_id,
            "agent": agent,
            "level": level,
            "event_type": event_type,
            "message": message,
            "metadata": metadata if isinstance(metadata, dict) else {},
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        with sqlite3.connect(self.database_path) as db:
            db.execute(
                "INSERT INTO agent_logs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    item["id"], item["project_id"], item["workflow_id"], item["task_id"],
                    item["agent"], item["level"], item["event_type"], item["message"],
                    json.dumps(item["metadata"], ensure_ascii=False), item["created_at"],
                ),
            )
        return item

    def list(
        self,
        *,
        project_id: str | None = None,
        task_id: str | None = None,
        agent: str | None = None,
        level: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, object]]:
        import json

        conditions: list[str] = []
        params: list[object] = []
        if project_id:
            conditions.append("project_id=?")
            params.append(project_id)
        if task_id:
            conditions.append("task_id=?")
            params.append(task_id)
        if agent:
            conditions.append("agent=?")
            params.append(agent)
        if level:
            conditions.append("level=?")
            params.append(level.lower())
        query = "SELECT * FROM agent_logs"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(max(1, min(int(limit), 500)))
        with sqlite3.connect(self.database_path) as db:
            db.row_factory = sqlite3.Row
            rows = db.execute(query, params).fetchall()
        result = []
        for row in rows:
            item = dict(row)
            try:
                item["metadata"] = json.loads(item["metadata"])
            except (TypeError, ValueError):
                item["metadata"] = {}
            result.append(item)
        return result
