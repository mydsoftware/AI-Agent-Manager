from __future__ import annotations

import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


class ProjectStore:
    """ذخیره‌ساز SQLite برای پروژه‌های پلتفرم با مالکیت پروژه."""

    def __init__(self, database_path: str = "data/platform.db") -> None:
        self.database_path = database_path
        Path(database_path).parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        """یک اتصال SQLite با Row factory ایجاد می‌کند."""
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        """Schema پروژه را ایجاد و migration مالکیت را انجام می‌دهد."""
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    request TEXT NOT NULL,
                    project_type TEXT NOT NULL,
                    is_private INTEGER NOT NULL,
                    repository TEXT,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    owner_id TEXT NOT NULL DEFAULT 'system'
                )
                """
            )
            columns = {row[1] for row in connection.execute("PRAGMA table_info(projects)").fetchall()}
            if "owner_id" not in columns:
                connection.execute("ALTER TABLE projects ADD COLUMN owner_id TEXT NOT NULL DEFAULT 'system'")

    @staticmethod
    def _slug(value: str) -> str:
        """نام پروژه را به slug امن برای repository محلی تبدیل می‌کند."""
        value = re.sub(r"[^\w\-]+", "-", value.strip().lower(), flags=re.UNICODE)
        return value.strip("-") or "project"

    @staticmethod
    def _request_owner(owner_id: str) -> str:
        """در HTTP از هویت احراز‌شده استفاده می‌کند و در مصرف مستقیم، مالک صریح را حفظ می‌کند."""
        try:
            from api.auth import current_principal
            principal = current_principal()
        except (RuntimeError, ImportError):
            principal = None
        if principal is not None:
            return principal.subject
        return str(owner_id).strip() or "system"

    @staticmethod
    def _request_owner_scope(owner_id: str | None) -> tuple[str | None, bool]:
        """Scope فهرست پروژه را از Principal جاری استخراج می‌کند؛ admin همه پروژه‌ها را می‌بیند."""
        if owner_id is not None:
            return str(owner_id).strip() or None, False
        try:
            from api.auth import current_principal
            principal = current_principal()
        except (RuntimeError, ImportError):
            principal = None
        if principal is None:
            return None, True
        return (None, True) if principal.role == "admin" else (principal.subject, False)

    @staticmethod
    def _request_owner_filter() -> str | None:
        """مالک پروژه را در HTTP برای defense-in-depth برمی‌گرداند؛ خارج از HTTP فیلتر نمی‌کند."""
        try:
            from api.auth import current_principal
            principal = current_principal()
        except (RuntimeError, ImportError):
            principal = None
        if principal is None or principal.role == "admin":
            return None
        return principal.subject

    def create(self, *, name: str, description: str, request: str,
               project_type: str = "website", is_private: bool = True,
               owner_id: str = "system") -> dict[str, object]:
        """پروژه را به مالک احراز‌شده درخواست جاری متصل می‌کند."""
        owner = self._request_owner(owner_id)
        project_id = str(uuid4())
        repository = f"local/{self._slug(name)}-{project_id[:8]}"
        created_at = datetime.now(timezone.utc).isoformat()
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO projects (id, name, description, request, project_type, is_private, repository, status, created_at, owner_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (project_id, name.strip(), description.strip(), request.strip(), project_type.strip() or "other", int(is_private), repository, "created", created_at, owner),
            )
        return self.get(project_id)  # type: ignore[return-value]

    def get(self, project_id: str) -> dict[str, object] | None:
        """یک پروژه را می‌خواند و در درخواست غیرادمین فقط پروژه مالک جاری را برمی‌گرداند."""
        owner_id = self._request_owner_filter()
        with self._connect() as connection:
            if owner_id is None:
                row = connection.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
            else:
                row = connection.execute(
                    "SELECT * FROM projects WHERE id = ? AND owner_id = ?",
                    (project_id, owner_id),
                ).fetchone()
        if row is None:
            return None
        result = dict(row)
        result["is_private"] = bool(result["is_private"])
        return result

    def set_status(self, project_id: str, status: str) -> dict[str, object] | None:
        """وضعیت چرخه عمر پروژه را به‌صورت اتمیک به‌روزرسانی می‌کند."""
        allowed = {"created", "planning", "running", "testing", "completed", "failed", "paused"}
        normalized = status.strip().lower()
        if normalized not in allowed:
            raise ValueError(f"وضعیت نامعتبر پروژه: {status}")
        owner_id = self._request_owner_filter()
        with self._connect() as connection:
            if owner_id is None:
                cursor = connection.execute("UPDATE projects SET status = ? WHERE id = ?", (normalized, project_id))
            else:
                cursor = connection.execute(
                    "UPDATE projects SET status = ? WHERE id = ? AND owner_id = ?",
                    (normalized, project_id, owner_id),
                )
            if cursor.rowcount == 0:
                return None
        return self.get(project_id)

    def list(self, owner_id: str | None = None, include_all: bool = False) -> list[dict[str, object]]:
        """پروژه‌ها را بر اساس owner جاری یا مالک صریح برمی‌گرداند."""
        scoped_owner, all_projects = self._request_owner_scope(owner_id)
        if include_all:
            all_projects = True
        with self._connect() as connection:
            if all_projects:
                rows = connection.execute("SELECT * FROM projects ORDER BY created_at DESC").fetchall()
            else:
                rows = connection.execute("SELECT * FROM projects WHERE owner_id = ? ORDER BY created_at DESC", (scoped_owner,)).fetchall()
        return [dict(row) for row in rows]
