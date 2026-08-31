"""سیستم مشاهده‌پذیری و ردیابی رویدادها."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class EventType(str, Enum):
    """انواع رویدادهای سیستم."""

    EXECUTION_STARTED = "execution_started"
    PLAN_CREATED = "plan_created"
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    RETRY_STARTED = "retry_started"
    REPLAN_STARTED = "replan_started"
    TOOL_CALL = "tool_call"
    LLM_REQUEST = "llm_request"
    LLM_RESPONSE = "llm_response"
    COMMIT_CREATED = "commit_created"
    CI_STARTED = "ci_started"
    CI_FAILED = "ci_failed"
    CI_FIXED = "ci_fixed"
    DEPLOY_STARTED = "deploy_started"
    DEPLOY_FAILED = "deploy_failed"
    DEPLOY_SUCCESS = "deploy_success"
    VERIFICATION_STARTED = "verification_started"
    VERIFICATION_SUCCESS = "verification_success"
    EXECUTION_COMPLETED = "execution_completed"
    EXECUTION_FAILED = "execution_failed"
    PROVIDER_FAILOVER = "provider_failover"
    LOOP_DETECTED = "loop_detected"
    SUPERVISOR_DECISION = "supervisor_decision"


@dataclass(frozen=True)
class Event:
    """یک رویداد ثبت‌شده."""

    id: str
    event_type: EventType
    execution_id: str
    task_id: str | None
    detail: dict[str, Any]
    timestamp: str


class Observability:
    """سیستم ردیابی و مشاهده رویدادها."""

    def __init__(self) -> None:
        self._events: list[Event] = []
        self._execution_id: str = ""

    def start_execution(self, request: str) -> str:
        """یک اجرای جدید را شروع می‌کند."""
        self._execution_id = f"exec-{uuid.uuid4().hex[:12]}"
        self._events = []
        self.record(EventType.EXECUTION_STARTED, {"request": request})
        return self._execution_id

    def record(
        self,
        event_type: EventType,
        detail: dict[str, Any] | None = None,
        task_id: str | None = None,
    ) -> Event:
        """یک رویداد را ثبت می‌کند."""
        event = Event(
            id=f"evt-{uuid.uuid4().hex[:8]}",
            event_type=event_type,
            execution_id=self._execution_id,
            task_id=task_id,
            detail=detail or {},
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        self._events.append(event)
        return event

    def complete_execution(self, success: bool = True) -> None:
        """اجرای جاری را تکمیل می‌کند."""
        event_type = EventType.EXECUTION_COMPLETED if success else EventType.EXECUTION_FAILED
        self.record(event_type, {"total_events": len(self._events)})

    def get_events(self, event_type: EventType | None = None, task_id: str | None = None) -> list[Event]:
        """رویدادها را فیلتر می‌کند."""
        events = self._events
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        if task_id:
            events = [e for e in events if e.task_id == task_id]
        return events

    def summary(self) -> dict[str, Any]:
        """خلاصه رویدادها را برمی‌گرداند."""
        counts: dict[str, int] = {}
        for event in self._events:
            key = event.event_type.value
            counts[key] = counts.get(key, 0) + 1
        return {
            "execution_id": self._execution_id,
            "total_events": len(self._events),
            "event_counts": counts,
        }

    def export(self) -> list[dict[str, Any]]:
        """تمام رویدادها را به فرمت dict برمی‌گرداند."""
        return [
            {
                "id": e.id,
                "event_type": e.event_type.value,
                "execution_id": e.execution_id,
                "task_id": e.task_id,
                "detail": e.detail,
                "timestamp": e.timestamp,
            }
            for e in self._events
        ]
