from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any


class PersistentMemory:
    """حافظه پایدار مبتنی بر SQLite برای نگهداری رویدادهای Manager."""

    def __init__(self, database_path: str = "data/manager.db") -> None:
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        """اتصال به پایگاه داده را ایجاد می‌کند."""
        return sqlite3.connect(self.database_path)

    def _initialize(self) -> None:
        """ساخت جدول حافظه را تضمین می‌کند."""
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event TEXT NOT NULL,
                    data TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def add(self, event: str, data: Any = None) -> None:
        """یک رویداد را به حافظه پایدار اضافه می‌کند."""
        encoded = json.dumps(data, ensure_ascii=False, default=str)
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO events (event, data) VALUES (?, ?)",
                (event, encoded),
            )

    def all(self) -> list[dict[str, Any]]:
        """رویدادهای ذخیره‌شده را از قدیمی به جدید برمی‌گرداند."""
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT id, event, data, created_at FROM events ORDER BY id"
            ).fetchall()

        return [
            {
                "id": row[0],
                "event": row[1],
                "data": json.loads(row[2]) if row[2] else None,
                "created_at": row[3],
            }
            for row in rows
        ]
