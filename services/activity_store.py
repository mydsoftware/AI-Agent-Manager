"""ذخیره‌سازی رویدادها و درخواست‌های تأیید پروژه."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


class ActivityStore:
    """Activity و Approval را در SQLite پایدار نگه می‌دارد."""

    def __init__(self, database_path: str = "data/platform.db") -> None:
        self.database_path = database_path
        Path(database_path).parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(database_path) as db:
            db.execute("CREATE TABLE IF NOT EXISTS activity (id TEXT PRIMARY KEY, project_id TEXT NOT NULL, event_type TEXT NOT NULL, message TEXT NOT NULL, created_at TEXT NOT NULL)")
            db.execute("CREATE TABLE IF NOT EXISTS approvals (id TEXT PRIMARY KEY, project_id TEXT NOT NULL, action TEXT NOT NULL, description TEXT NOT NULL, status TEXT NOT NULL, created_at TEXT NOT NULL, resolved_at TEXT)")

    def add(self, project_id: str, event_type: str, message: str) -> dict[str, object]:
        item = (str(uuid4()), project_id, event_type, message, datetime.now(timezone.utc).isoformat())
        with sqlite3.connect(self.database_path) as db:
            db.execute("INSERT INTO activity VALUES (?, ?, ?, ?, ?)", item)
        return {"id": item[0], "project_id": item[1], "event_type": item[2], "message": item[3], "created_at": item[4]}

    def list(self, project_id: str, limit: int = 100) -> list[dict[str, object]]:
        with sqlite3.connect(self.database_path) as db:
            db.row_factory = sqlite3.Row
            rows = db.execute("SELECT * FROM activity WHERE project_id=? ORDER BY created_at DESC LIMIT ?", (project_id, max(1, min(limit, 500)))).fetchall()
        return [dict(row) for row in rows]

    def create_approval(self, project_id: str, action: str, description: str) -> dict[str, object]:
        approval_id = str(uuid4())
        created = datetime.now(timezone.utc).isoformat()
        with sqlite3.connect(self.database_path) as db:
            db.execute("INSERT INTO approvals VALUES (?, ?, ?, ?, 'pending', ?, NULL)", (approval_id, project_id, action, description, created))
        return self.get_approval(approval_id)  # type: ignore[return-value]

    def get_approval(self, approval_id: str) -> dict[str, object] | None:
        with sqlite3.connect(self.database_path) as db:
            db.row_factory = sqlite3.Row
            row = db.execute("SELECT * FROM approvals WHERE id=?", (approval_id,)).fetchone()
        return dict(row) if row else None

    def approvals(self, project_id: str | None = None) -> list[dict[str, object]]:
        with sqlite3.connect(self.database_path) as db:
            db.row_factory = sqlite3.Row
            if project_id:
                rows = db.execute("SELECT * FROM approvals WHERE project_id=? ORDER BY created_at DESC", (project_id,)).fetchall()
            else:
                rows = db.execute("SELECT * FROM approvals ORDER BY created_at DESC").fetchall()
        return [dict(row) for row in rows]

    def resolve_approval(self, approval_id: str, status: str) -> dict[str, object] | None:
        if status not in {"approved", "rejected"}:
            raise ValueError("وضعیت تأیید باید approved یا rejected باشد.")
        resolved = datetime.now(timezone.utc).isoformat()
        with sqlite3.connect(self.database_path) as db:
            cursor = db.execute("UPDATE approvals SET status=?, resolved_at=? WHERE id=? AND status='pending'", (status, resolved, approval_id))
            if cursor.rowcount == 0:
                return None
        return self.get_approval(approval_id)
