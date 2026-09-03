"""ذخیره‌سازی پایدار Workflowهای پروژه."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class WorkflowStore:
    """Workflow plan را به‌صورت JSON در SQLite نگه می‌دارد."""

    def __init__(self, database_path: str = "data/platform.db") -> None:
        self.database_path = database_path
        Path(database_path).parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS project_workflows (
                    project_id TEXT PRIMARY KEY,
                    workflow_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )

    def get(self, project_id: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT workflow_json, updated_at FROM project_workflows WHERE project_id = ?",
                (project_id,),
            ).fetchone()
        if row is None:
            return None
        return {"project_id": project_id, "workflow": json.loads(row["workflow_json"]), "updated_at": row["updated_at"]}

    def save(self, project_id: str, workflow: dict[str, Any]) -> dict[str, Any]:
        updated_at = datetime.now(timezone.utc).isoformat()
        payload = json.dumps(workflow, ensure_ascii=False)
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO project_workflows (project_id, workflow_json, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(project_id) DO UPDATE SET workflow_json = excluded.workflow_json, updated_at = excluded.updated_at
                """ ,
                (project_id, payload, updated_at),
            )
        return self.get(project_id)  # type: ignore[return-value]

    def delete(self, project_id: str) -> bool:
        with self._connect() as connection:
            cursor = connection.execute("DELETE FROM project_workflows WHERE project_id = ?", (project_id,))
        return cursor.rowcount > 0
