"""ذخیره‌سازی پایدار Workflowهای پروژه."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class WorkflowStore:
    """Workflow plan و State اجرای آن را به‌صورت پایدار در SQLite نگه می‌دارد."""

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
            columns = {row[1] for row in connection.execute("PRAGMA table_info(project_workflows)").fetchall()}
            migrations = {
                "state": "ALTER TABLE project_workflows ADD COLUMN state TEXT NOT NULL DEFAULT 'planned'",
                "attempts": "ALTER TABLE project_workflows ADD COLUMN attempts INTEGER NOT NULL DEFAULT 0",
                "last_error": "ALTER TABLE project_workflows ADD COLUMN last_error TEXT",
            }
            for column, statement in migrations.items():
                if column not in columns:
                    connection.execute(statement)

    def get(self, project_id: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT workflow_json, updated_at, state, attempts, last_error FROM project_workflows WHERE project_id = ?",
                (project_id,),
            ).fetchone()
        if row is None:
            return None
        return {
            "project_id": project_id,
            "workflow": json.loads(row["workflow_json"]),
            "updated_at": row["updated_at"],
            "state": row["state"],
            "attempts": int(row["attempts"] or 0),
            "last_error": row["last_error"],
        }

    def save(
        self,
        project_id: str,
        workflow: dict[str, Any],
        state: str | None = None,
        attempts: int | None = None,
        last_error: str | None = None,
    ) -> dict[str, Any]:
        """Workflow را ذخیره می‌کند و State قبلی را در صورت عدم ارسال حفظ می‌کند."""
        updated_at = datetime.now(timezone.utc).isoformat()
        payload = json.dumps(workflow, ensure_ascii=False)
        current = self.get(project_id)
        effective_state = state if state is not None else (current.get("state", "planned") if current else "planned")
        effective_attempts = max(0, int(attempts if attempts is not None else (current.get("attempts", 0) if current else 0)))
        effective_error = last_error if last_error is not None else (current.get("last_error") if current else None)
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO project_workflows (project_id, workflow_json, updated_at, state, attempts, last_error)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(project_id) DO UPDATE SET
                    workflow_json = excluded.workflow_json,
                    updated_at = excluded.updated_at,
                    state = excluded.state,
                    attempts = excluded.attempts,
                    last_error = excluded.last_error
                """,
                (project_id, payload, updated_at, effective_state, effective_attempts, effective_error),
            )
        return self.get(project_id)  # type: ignore[return-value]

    def transition(
        self,
        project_id: str,
        state: str,
        *,
        attempts: int | None = None,
        last_error: str | None = None,
    ) -> dict[str, Any] | None:
        """State را اتمیک و بدون بازنویسی Workflow تغییر می‌دهد."""
        current = self.get(project_id)
        if current is None:
            return None
        next_attempts = int(current.get("attempts", 0)) if attempts is None else max(0, int(attempts))
        updated_at = datetime.now(timezone.utc).isoformat()
        with self._connect() as connection:
            connection.execute(
                "UPDATE project_workflows SET state = ?, attempts = ?, last_error = ?, updated_at = ? WHERE project_id = ?",
                (state.strip() or "planned", next_attempts, last_error, updated_at, project_id),
            )
        return self.get(project_id)

    def delete(self, project_id: str) -> bool:
        with self._connect() as connection:
            cursor = connection.execute("DELETE FROM project_workflows WHERE project_id = ?", (project_id,))
        return cursor.rowcount > 0
