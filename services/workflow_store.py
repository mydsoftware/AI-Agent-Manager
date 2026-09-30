"""ذخیره‌سازی پایدار Workflow و checkpoint اجرای پروژه."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class WorkflowStore:
    """Workflow plan و checkpoint اجرای آن را به‌صورت پایدار در SQLite نگه می‌دارد."""

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
            connection.execute("""
                CREATE TABLE IF NOT EXISTS project_workflows (
                    project_id TEXT PRIMARY KEY,
                    workflow_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            columns = {row[1] for row in connection.execute("PRAGMA table_info(project_workflows)").fetchall()}
            migrations = {
                "state": "ALTER TABLE project_workflows ADD COLUMN state TEXT NOT NULL DEFAULT 'planned'",
                "attempts": "ALTER TABLE project_workflows ADD COLUMN attempts INTEGER NOT NULL DEFAULT 0",
                "last_error": "ALTER TABLE project_workflows ADD COLUMN last_error TEXT",
                "phase": "ALTER TABLE project_workflows ADD COLUMN phase TEXT NOT NULL DEFAULT 'planned'",
                "current_task": "ALTER TABLE project_workflows ADD COLUMN current_task TEXT",
                "head_sha": "ALTER TABLE project_workflows ADD COLUMN head_sha TEXT",
                "preview_url": "ALTER TABLE project_workflows ADD COLUMN preview_url TEXT",
            }
            for column, statement in migrations.items():
                if column not in columns:
                    connection.execute(statement)

    def get(self, project_id: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(
                """SELECT workflow_json, updated_at, state, attempts, last_error,
                          phase, current_task, head_sha, preview_url
                   FROM project_workflows WHERE project_id = ?""",
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
            "phase": row["phase"],
            "current_task": row["current_task"],
            "head_sha": row["head_sha"],
            "preview_url": row["preview_url"],
        }

    def save(
        self,
        project_id: str,
        workflow: dict[str, Any],
        state: str | None = None,
        attempts: int | None = None,
        last_error: str | None = None,
        phase: str | None = None,
        current_task: str | None = None,
        head_sha: str | None = None,
        preview_url: str | None = None,
    ) -> dict[str, Any]:
        """Workflow را ذخیره می‌کند و checkpoint قبلی را در صورت عدم ارسال حفظ می‌کند."""
        updated_at = datetime.now(timezone.utc).isoformat()
        payload = json.dumps(workflow, ensure_ascii=False)
        current = self.get(project_id)
        effective_state = state if state is not None else (current.get("state", "planned") if current else "planned")
        effective_attempts = max(0, int(attempts if attempts is not None else (current.get("attempts", 0) if current else 0)))
        effective_error = last_error if last_error is not None else (current.get("last_error") if current else None)
        effective_phase = phase if phase is not None else (current.get("phase", "planned") if current else "planned")
        effective_task = current.get("current_task") if current else None if current else None
        if current_task is not None:
            effective_task = current_task
        effective_head = head_sha if head_sha is not None else (current.get("head_sha") if current else None)
        effective_preview = preview_url if preview_url is not None else (current.get("preview_url") if current else None)
        with self._connect() as connection:
            connection.execute("""
                INSERT INTO project_workflows
                (project_id, workflow_json, updated_at, state, attempts, last_error,
                 phase, current_task, head_sha, preview_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(project_id) DO UPDATE SET
                    workflow_json = excluded.workflow_json,
                    updated_at = excluded.updated_at,
                    state = excluded.state,
                    attempts = excluded.attempts,
                    last_error = excluded.last_error,
                    phase = excluded.phase,
                    current_task = excluded.current_task,
                    head_sha = excluded.head_sha,
                    preview_url = excluded.preview_url
            """, (project_id, payload, updated_at, effective_state, effective_attempts,
                  effective_error, effective_phase, effective_task, effective_head, effective_preview))
        return self.get(project_id)  # type: ignore[return-value]

    def transition(
        self,
        project_id: str,
        state: str,
        *,
        attempts: int | None = None,
        last_error: str | None = None,
        phase: str | None = None,
        current_task: str | None = None,
        head_sha: str | None = None,
        preview_url: str | None = None,
    ) -> dict[str, Any] | None:
        """State و checkpoint را اتمیک تغییر می‌دهد؛ مقادیر ارسال‌نشده حفظ می‌شوند."""
        current = self.get(project_id)
        if current is None:
            return None
        next_attempts = int(current.get("attempts", 0)) if attempts is None else max(0, int(attempts))
        next_phase = current.get("phase", "planned") if phase is None else phase.strip() or "planned"
        next_task = current.get("current_task") if current_task is None else current_task
        next_head = current.get("head_sha") if head_sha is None else head_sha
        next_preview = current.get("preview_url") if preview_url is None else preview_url
        updated_at = datetime.now(timezone.utc).isoformat()
        with self._connect() as connection:
            connection.execute("""
                UPDATE project_workflows
                SET state = ?, attempts = ?, last_error = ?, phase = ?, current_task = ?,
                    head_sha = ?, preview_url = ?, updated_at = ?
                WHERE project_id = ?
            """, (state.strip() or "planned", next_attempts, last_error, next_phase,
                  next_task, next_head, next_preview, updated_at, project_id))
        return self.get(project_id)

    def delete(self, project_id: str) -> bool:
        with self._connect() as connection:
            cursor = connection.execute("DELETE FROM project_workflows WHERE project_id = ?", (project_id,))
        return cursor.rowcount > 0
