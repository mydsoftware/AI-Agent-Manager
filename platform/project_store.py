from __future__ import annotations

import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


class ProjectStore:
    """ذخیره‌ساز SQLite برای پروژه‌های پلتفرم."""

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
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    request TEXT NOT NULL,
                    project_type TEXT NOT NULL,
                    is_private INTEGER NOT NULL,
                    repository TEXT,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )

    @staticmethod
    def _slug(value: str) -> str:
        value = re.sub(r"[^\w\-]+", "-", value.strip().lower(), flags=re.UNICODE)
        return value.strip("-") or "project"

    def create(
        self,
        *,
        name: str,
        description: str,
        request: str,
        project_type: str = "website",
        is_private: bool = True,
    ) -> dict[str, object]:
        project_id = str(uuid4())
        repository = f"local/{self._slug(name)}-{project_id[:8]}"
        created_at = datetime.now(timezone.utc).isoformat()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO projects
                (id, name, description, request, project_type, is_private, repository, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    project_id,
                    name.strip(),
                    description.strip(),
                    request.strip(),
                    project_type.strip() or "other",
                    int(is_private),
                    repository,
                    "created",
                    created_at,
                ),
            )
        return self.get(project_id)  # type: ignore[return-value]

    def get(self, project_id: str) -> dict[str, object] | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM projects WHERE id = ?", (project_id,)
            ).fetchone()
        if row is None:
            return None
        result = dict(row)
        result["is_private"] = bool(result["is_private"])
        return result

    def list(self) -> list[dict[str, object]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM projects ORDER BY created_at DESC"
            ).fetchall()
        return [dict(row) for row in rows]
