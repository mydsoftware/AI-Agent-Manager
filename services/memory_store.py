from __future__ import annotations
import json, sqlite3
from pathlib import Path
from typing import Any

class MemoryStore:
    """حافظه ساختاریافته و قابل مدیریت برای scopeهای مختلف."""
    SCOPES = {"user", "workspace", "project", "agent", "workflow", "global"}
    def __init__(self, database_path: str = "data/manager.db") -> None:
        self.database_path = Path(database_path); self.database_path.parent.mkdir(parents=True, exist_ok=True); self._initialize()
    def _connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.database_path); db.row_factory = sqlite3.Row; return db
    def _initialize(self) -> None:
        with self._connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS memories (id INTEGER PRIMARY KEY AUTOINCREMENT, scope TEXT NOT NULL, scope_id TEXT NOT NULL DEFAULT '', key TEXT NOT NULL, value TEXT NOT NULL, importance INTEGER NOT NULL DEFAULT 5, source TEXT NOT NULL DEFAULT 'user', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, UNIQUE(scope, scope_id, key))")
            db.execute("CREATE INDEX IF NOT EXISTS idx_memories_scope ON memories(scope, scope_id)")
    def upsert(self, scope: str, scope_id: str, key: str, value: Any, importance: int = 5, source: str = "user") -> dict[str, Any]:
        scope, scope_id, key = scope.strip().lower(), scope_id.strip(), key.strip()
        if scope not in self.SCOPES: raise ValueError("scope نامعتبر است.")
        if not key: raise ValueError("key الزامی است.")
        encoded = json.dumps(value, ensure_ascii=False, default=str); importance = max(1, min(10, int(importance)))
        with self._connect() as db:
            db.execute("INSERT INTO memories(scope,scope_id,key,value,importance,source) VALUES(?,?,?,?,?,?) ON CONFLICT(scope,scope_id,key) DO UPDATE SET value=excluded.value,importance=excluded.importance,source=excluded.source,updated_at=CURRENT_TIMESTAMP", (scope,scope_id,key,encoded,importance,source.strip() or "user"))
            row = db.execute("SELECT * FROM memories WHERE scope=? AND scope_id=? AND key=?", (scope,scope_id,key)).fetchone()
        return self._row(row)
    def list(self, scope: str | None = None, scope_id: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        query="SELECT * FROM memories"; params=[]; where=[]
        if scope:
            if scope not in self.SCOPES: raise ValueError("scope نامعتبر است.")
            where.append("scope=?"); params.append(scope)
        if scope_id is not None: where.append("scope_id=?"); params.append(scope_id)
        if where: query += " WHERE " + " AND ".join(where)
        query += " ORDER BY importance DESC, updated_at DESC LIMIT ?"; params.append(max(1,min(int(limit),500)))
        with self._connect() as db: rows=db.execute(query,params).fetchall()
        return [self._row(r) for r in rows]
    def get(self, memory_id: int) -> dict[str, Any] | None:
        with self._connect() as db: row=db.execute("SELECT * FROM memories WHERE id=?",(memory_id,)).fetchone()
        return self._row(row) if row else None
    def delete(self, memory_id: int) -> bool:
        with self._connect() as db: cur=db.execute("DELETE FROM memories WHERE id=?",(memory_id,))
        return cur.rowcount > 0
    @staticmethod
    def _row(row: sqlite3.Row) -> dict[str, Any]:
        item=dict(row); item["value"]=json.loads(item["value"]); return item
