from __future__ import annotations

from services.agent_log_store import AgentLogStore


def test_agent_log_store_persists_and_filters(tmp_path):
    store = AgentLogStore(str(tmp_path / "logs.db"))
    created = store.add(
        "developer",
        "task.started",
        "Task شروع شد",
        project_id="p1",
        task_id="t1",
        metadata={"attempt": 1},
    )
    store.add("qa", "task.failed", "تست ناموفق بود", project_id="p2", level="error")

    assert created["agent"] == "developer"
    assert created["metadata"] == {"attempt": 1}
    assert len(store.list(project_id="p1")) == 1
    assert store.list(project_id="p1")[0]["metadata"] == {"attempt": 1}
    assert store.list(agent="qa", level="error")[0]["event_type"] == "task.failed"


def test_agent_log_store_validates_input(tmp_path):
    store = AgentLogStore(str(tmp_path / "logs.db"))
    try:
        store.add("", "task.started", "x")
    except ValueError as error:
        assert "agent" in str(error)
    else:
        raise AssertionError("invalid agent should fail")

    try:
        store.add("developer", "task.started", "x", level="fatal")
    except ValueError as error:
        assert "level" in str(error)
    else:
        raise AssertionError("invalid level should fail")
