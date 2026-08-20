from __future__ import annotations

import json

from manager.execution_store import ExecutionStore


def test_execution_store_lifecycle(tmp_path):
    store = ExecutionStore(str(tmp_path / "executions"))
    created = store.create("123e4567-e89b-12d3-a456-426614174000", "req-1", "website-audit", "https://example.com")
    assert created.status == "accepted"

    running = store.update(created.execution_id, status="running")
    assert running.status == "running"

    completed = store.update(created.execution_id, status="completed", result={"report": "گزارش آزمایشی"})
    loaded = store.get(created.execution_id)
    assert loaded.status == "completed"
    assert loaded.result == {"report": "گزارش آزمایشی"}

    raw = json.loads((tmp_path / "executions" / f"{created.execution_id}.json").read_text(encoding="utf-8"))
    assert raw["request_id"] == "req-1"
    assert raw["url"] == "https://example.com"
