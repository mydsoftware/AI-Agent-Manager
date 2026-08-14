from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from manager.task import Task
from manager.task_status import TaskStatus


class SupervisorAction(str, Enum):
    """اقدام بعدی Supervisor را مشخص می‌کند."""

    CONTINUE = "continue"
    RETRY = "retry"
    STOP = "stop"
    SKIP = "skip"


@dataclass
class SupervisorDecision:
    """تصمیم Supervisor درباره مرحله بعدی اجرای Manager."""

    action: SupervisorAction
    reason: str


class Supervisor:
    """نتیجه هر Task را بررسی و مسیر اجرای Manager را کنترل می‌کند."""

    def decide(self, task: Task) -> SupervisorDecision:
        """بر اساس وضعیت Task اقدام بعدی را انتخاب می‌کند."""
        if task.status == TaskStatus.SUCCESS and task.result:
            return SupervisorDecision(SupervisorAction.CONTINUE, "Task با موفقیت تکمیل شد.")
        if task.status == TaskStatus.FAILED:
            return SupervisorDecision(SupervisorAction.RETRY, "Task ناموفق بود و نیاز به تلاش اصلاحی دارد.")
        if task.status == TaskStatus.BLOCKED:
            return SupervisorDecision(SupervisorAction.STOP, "Task به دلیل وابستگی مسدود شده است.")
        return SupervisorDecision(SupervisorAction.STOP, "وضعیت Task برای ادامه معتبر نیست.")
