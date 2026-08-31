"""Local SQLite/JSON traces for multi-agent runs."""

from __future__ import annotations

import json
import logging
import sqlite3
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class TraceRecord:
    id: str
    project_id: str
    task_id: str
    agent: str
    event: str
    payload: dict[str, Any] = field(default_factory=dict)
    tokens: int = 0
    cost_usd: float = 0.0
    model: str = ""
    provider: str = ""
    duration_ms: float = 0.0
    error: str | None = None
    created_at: float = field(default_factory=time.time)


class Tracer:
    def __init__(self, path: str = "data/traces.db") -> None:
        self.path = path
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS traces (
                    id TEXT PRIMARY KEY,
                    project_id TEXT,
                    task_id TEXT,
                    agent TEXT,
                    event TEXT,
                    payload TEXT,
                    tokens INTEGER,
                    cost_usd REAL,
                    model TEXT,
                    provider TEXT,
                    duration_ms REAL,
                    error TEXT,
                    created_at REAL
                )
                """
            )

    def emit(self, **kwargs: Any) -> TraceRecord:
        rec = TraceRecord(id=str(uuid.uuid4()), **kwargs)
        with sqlite3.connect(self.path) as conn:
            conn.execute(
                "INSERT INTO traces VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    rec.id, rec.project_id, rec.task_id, rec.agent, rec.event,
                    json.dumps(rec.payload, ensure_ascii=False, default=str),
                    rec.tokens, rec.cost_usd, rec.model, rec.provider,
                    rec.duration_ms, rec.error, rec.created_at,
                ),
            )
        logger.debug("trace %s %s %s", rec.agent, rec.event, rec.task_id)
        return rec

    def task_summary(self, task_id: str) -> dict[str, Any]:
        rows = self._query("SELECT * FROM traces WHERE task_id=? ORDER BY created_at", (task_id,))
        tokens = sum(r["tokens"] or 0 for r in rows)
        cost = sum(r["cost_usd"] or 0 for r in rows)
        errors = [r for r in rows if r["error"]]
        return {"task_id": task_id, "events": len(rows), "tokens": tokens, "cost_usd": cost, "errors": len(errors), "rows": rows}

    def agent_activity(self, agent: str | None = None) -> list[dict[str, Any]]:
        if agent:
            return self._query("SELECT * FROM traces WHERE agent=? ORDER BY created_at DESC LIMIT 200", (agent,))
        return self._query("SELECT * FROM traces ORDER BY created_at DESC LIMIT 200", ())

    def token_report(self) -> dict[str, int]:
        rows = self._query("SELECT agent, SUM(tokens) AS t FROM traces GROUP BY agent", ())
        return {r["agent"]: int(r["t"] or 0) for r in rows}

    def error_report(self) -> list[dict[str, Any]]:
        return self._query("SELECT * FROM traces WHERE error IS NOT NULL AND error != '' ORDER BY created_at DESC LIMIT 100", ())

    def _query(self, sql: str, args: tuple) -> list[dict[str, Any]]:
        with sqlite3.connect(self.path) as conn:
            conn.row_factory = sqlite3.Row
            return [dict(r) for r in conn.execute(sql, args)]
