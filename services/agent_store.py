from __future__ import annotations

import re
import sqlite3
from pathlib import Path
from uuid import uuid4


class AgentStore:
    """تعریف ایجنت‌های ساخته‌شده توسط کاربر را به‌صورت پایدار نگه می‌دارد."""

    def __init__(self, database_path: str = "data/manager.db") -> None:
        self.database_path = database_path
        Path(database_path).parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(database_path) as connection:
            connection.execute(
                """CREATE TABLE IF NOT EXISTS custom_agents (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT NOT NULL,
                    system_prompt TEXT NOT NULL,
                    capabilities TEXT NOT NULL,
                    enabled INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )"""
            )
            connection.commit()

    def list(self) -> list[dict[str, object]]:
        with sqlite3.connect(self.database_path) as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(
                "SELECT * FROM custom_agents ORDER BY created_at DESC"
            ).fetchall()
        return [dict(row) for row in rows]

    def get(self, name: str) -> dict[str, object] | None:
        with sqlite3.connect(self.database_path) as connection:
            connection.row_factory = sqlite3.Row
            row = connection.execute(
                "SELECT * FROM custom_agents WHERE name = ?", (name,)
            ).fetchone()
        return dict(row) if row else None

    def create(self, name: str, description: str, system_prompt: str, capabilities: list[str]) -> dict[str, object]:
        slug = re.sub(r"[^a-z0-9_-]+", "-", name.lower()).strip("-")
        if not slug:
            raise ValueError("نام ایجنت باید حداقل یک حرف یا عدد لاتین داشته باشد.")
        if len(slug) > 50:
            slug = slug[:50].rstrip("-")
        with sqlite3.connect(self.database_path) as connection:
            try:
                connection.execute(
                    "INSERT INTO custom_agents (id, name, description, system_prompt, capabilities) VALUES (?, ?, ?, ?, ?)",
                    (str(uuid4()), slug, description.strip(), system_prompt.strip(), ",".join(capabilities)),
                )
                connection.commit()
            except sqlite3.IntegrityError as error:
                raise ValueError("ایجنتی با این نام از قبل وجود دارد.") from error
        return self.get(slug)  # type: ignore[return-value]

    def delete(self, name: str) -> bool:
        with sqlite3.connect(self.database_path) as connection:
            cursor = connection.execute("DELETE FROM custom_agents WHERE name = ?", (name,))
            connection.commit()
            return cursor.rowcount > 0
