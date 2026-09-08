"""ذخیره‌سازی رویدادها و درخواست‌های تأیید پروژه."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


class ActivityStore:
    """Activity و Approval را در SQLite پایدار نگه می‌دارد."""

    ACTIVE_APPROVAL_STATUSES = ("pending", "approved", "claimed")

    def __init__(self, database_path: str = "data/platform.db") -> None:
        self.database_path = database_path
        Path(database_path).parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(database_path) as db:
            db.execute("CREATE TABLE IF NOT EXISTS activity (id TEXT PRIMARY KEY, project_id TEXT NOT NULL, event_type TEXT NOT NULL, message TEXT NOT NULL, created_at TEXT NOT NULL)")
            db.execute("CREATE TABLE IF NOT EXISTS approvals (id TEXT PRIMARY KEY, project_id TEXT NOT NULL, action TEXT NOT NULL, description TEXT NOT NULL, status TEXT NOT NULL, created_at TEXT NOT NULL, resolved_at TEXT, fingerprint TEXT)")
            columns = {row[1] for row in db.execute("PRAGMA table_info(approvals)").fetchall()}
            if "fingerprint" not in columns:
                db.execute("ALTER TABLE approvals ADD COLUMN fingerprint TEXT")
            db.execute("CREATE INDEX IF NOT EXISTS idx_approvals_project_fingerprint ON approvals(project_id, fingerprint)")

    def add(self, project_id: str, event_type: str, message: str) -> dict[str, object]:
        """یک رویداد را در Activity ثبت می‌کند."""
        item = (str(uuid4()), project_id, event_type, message, datetime.now(timezone.utc).isoformat())
        with sqlite3.connect(self.database_path) as db:
            db.execute("INSERT INTO activity VALUES (?, ?, ?, ?, ?)", item)
        return {"id": item[0], "project_id": item[1], "event_type": item[2], "message": item[3], "created_at": item[4]}

    def list(self, project_id: str, limit: int = 100) -> list[dict[str, object]]:
        """رویدادهای یک پروژه را با سقف خروجی محدود برمی‌گرداند."""
        with sqlite3.connect(self.database_path) as db:
            db.row_factory = sqlite3.Row
            rows = db.execute("SELECT * FROM activity WHERE project_id=? ORDER BY created_at DESC LIMIT ?", (project_id, max(1, min(limit, 500)))).fetchall()
        return [dict(row) for row in rows]

    def create_approval(self, project_id: str, action: str, description: str, fingerprint: str | None = None) -> dict[str, object]:
        """Approval فعال را برای fingerprint یکتا ایجاد یا رکورد فعال موجود را برمی‌گرداند."""
        created = datetime.now(timezone.utc).isoformat()
        with sqlite3.connect(self.database_path, timeout=10.0) as db:
            db.execute("BEGIN IMMEDIATE")
            if fingerprint:
                row = db.execute(
                    "SELECT * FROM approvals WHERE project_id=? AND fingerprint=? AND status IN ('pending','approved','claimed') ORDER BY created_at DESC LIMIT 1",
                    (project_id, fingerprint),
                ).fetchone()
                if row:
                    columns = [item[1] for item in db.execute("PRAGMA table_info(approvals)").fetchall()]
                    return dict(zip(columns, row))
            approval_id = str(uuid4())
            try:
                db.execute(
                    "INSERT INTO approvals (id, project_id, action, description, status, created_at, resolved_at, fingerprint) VALUES (?, ?, ?, ?, 'pending', ?, NULL, ?)",
                    (approval_id, project_id, action, description, created, fingerprint),
                )
            except sqlite3.IntegrityError:
                if not fingerprint:
                    raise
                row = db.execute(
                    "SELECT * FROM approvals WHERE project_id=? AND fingerprint=? AND status IN ('pending','approved','claimed') ORDER BY created_at DESC LIMIT 1",
                    (project_id, fingerprint),
                ).fetchone()
                if not row:
                    raise
                columns = [item[1] for item in db.execute("PRAGMA table_info(approvals)").fetchall()]
                return dict(zip(columns, row))
        return self.get_approval(approval_id)  # type: ignore[return-value]

    def get_approval(self, approval_id: str) -> dict[str, object] | None:
        """یک Approval را بر اساس شناسه می‌خواند."""
        with sqlite3.connect(self.database_path) as db:
            db.row_factory = sqlite3.Row
            row = db.execute("SELECT * FROM approvals WHERE id=?", (approval_id,)).fetchone()
        return dict(row) if row else None

    def approvals(self, project_id: str | None = None) -> list[dict[str, object]]:
        """Approvalهای پروژه یا کل سیستم را بدون تغییر وضعیت برمی‌گرداند."""
        with sqlite3.connect(self.database_path) as db:
            db.row_factory = sqlite3.Row
            if project_id:
                rows = db.execute("SELECT * FROM approvals WHERE project_id=? ORDER BY created_at DESC", (project_id,)).fetchall()
            else:
                rows = db.execute("SELECT * FROM approvals ORDER BY created_at DESC").fetchall()
        return [dict(row) for row in rows]

    def resolve_approval(self, approval_id: str, status: str) -> dict[str, object] | None:
        """Approval pending را فقط یک‌بار به approved یا rejected تبدیل می‌کند."""
        if status not in {"approved", "rejected"}:
            raise ValueError("وضعیت تأیید باید approved یا rejected باشد.")
        resolved = datetime.now(timezone.utc).isoformat()
        with sqlite3.connect(self.database_path, timeout=10.0) as db:
            cursor = db.execute("UPDATE approvals SET status=?, resolved_at=? WHERE id=? AND status='pending'", (status, resolved, approval_id))
            if cursor.rowcount == 0:
                return None
        return self.get_approval(approval_id)

    def claim_approval(self, approval_id: str, fingerprint: str) -> dict[str, object] | None:
        """Approval تأییدشده را به‌صورت اتمیک Claim می‌کند تا اجرای همزمان فقط یک برنده داشته باشد."""
        claimed_at = datetime.now(timezone.utc).isoformat()
        with sqlite3.connect(self.database_path, timeout=10.0) as db:
            cursor = db.execute(
                "UPDATE approvals SET status='claimed', resolved_at=? WHERE id=? AND status='approved' AND fingerprint=?",
                (claimed_at, approval_id, fingerprint),
            )
            if cursor.rowcount == 0:
                return None
        return self.get_approval(approval_id)

    def release_approval(self, approval_id: str, fingerprint: str) -> dict[str, object] | None:
        """Approval Claim‌شده را پس از شکست اجرا، فقط در صورت تطابق fingerprint آزاد می‌کند."""
        with sqlite3.connect(self.database_path, timeout=10.0) as db:
            cursor = db.execute(
                "UPDATE approvals SET status='approved', resolved_at=? WHERE id=? AND status='claimed' AND fingerprint=?",
                (datetime.now(timezone.utc).isoformat(), approval_id, fingerprint),
            )
            if cursor.rowcount == 0:
                return None
        return self.get_approval(approval_id)

    def consume_approval(self, approval_id: str) -> dict[str, object] | None:
        """Approval Claim‌شده را پس از اجرای موفق یک‌بار مصرف می‌کند."""
        resolved = datetime.now(timezone.utc).isoformat()
        with sqlite3.connect(self.database_path, timeout=10.0) as db:
            cursor = db.execute("UPDATE approvals SET status='consumed', resolved_at=? WHERE id=? AND status='claimed'", (resolved, approval_id))
            if cursor.rowcount == 0:
                return None
        return self.get_approval(approval_id)
