"""تست‌های سیستم مشاهده‌پذیری."""

from __future__ import annotations

from manager.observability import Event, EventType, Observability


def test_start_execution() -> None:
    """شروع یک اجرای جدید."""
    obs = Observability()
    exec_id = obs.start_execution("test request")
    assert exec_id.startswith("exec-")
    assert len(obs.get_events()) == 1
    assert obs.get_events()[0].event_type == EventType.EXECUTION_STARTED


def test_record_event() -> None:
    """ثبت رویداد."""
    obs = Observability()
    obs.start_execution("test")
    event = obs.record(EventType.TASK_STARTED, {"task_id": "t1"}, task_id="t1")
    assert event.id.startswith("evt-")
    assert event.event_type == EventType.TASK_STARTED
    assert event.task_id == "t1"


def test_complete_execution() -> None:
    """تکمیل اجرا."""
    obs = Observability()
    obs.start_execution("test")
    obs.record(EventType.TASK_STARTED)
    obs.record(EventType.TASK_COMPLETED)
    obs.complete_execution(True)

    events = obs.get_events()
    assert len(events) == 4  # started + task_started + task_completed + execution_completed
    assert events[-1].event_type == EventType.EXECUTION_COMPLETED


def test_get_events_filter() -> None:
    """فیلتر رویدادها."""
    obs = Observability()
    obs.start_execution("test")
    obs.record(EventType.TASK_STARTED, task_id="t1")
    obs.record(EventType.TASK_COMPLETED, task_id="t1")
    obs.record(EventType.TASK_STARTED, task_id="t2")

    t1_events = obs.get_events(task_id="t1")
    assert len(t1_events) == 2

    started = obs.get_events(event_type=EventType.TASK_STARTED)
    assert len(started) == 2


def test_summary() -> None:
    """خلاصه رویدادها."""
    obs = Observability()
    obs.start_execution("test")
    obs.record(EventType.TASK_STARTED)
    obs.record(EventType.TASK_COMPLETED)
    obs.complete_execution(True)

    summary = obs.summary()
    assert summary["total_events"] == 4  # started + task_started + task_completed + completed
    assert "task_started" in summary["event_counts"]


def test_export() -> None:
    """خروجی JSON."""
    obs = Observability()
    obs.start_execution("test")
    obs.record(EventType.TOOL_CALL, {"tool": "filesystem"})

    export = obs.export()
    assert len(export) == 2
    assert export[0]["event_type"] == "execution_started"
    assert export[1]["detail"]["tool"] == "filesystem"
