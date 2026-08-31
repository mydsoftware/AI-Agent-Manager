"""کنترل‌کننده اجرای Manager."""

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
    REPLAN = "replan"


@dataclass
class SupervisorDecision:
    """تصمیم Supervisor درباره مرحله بعدی اجرای Manager."""

    action: SupervisorAction
    reason: str


class Supervisor:
    """نتیجه هر Task را بررسی و مسیر اجرای Manager را کنترل می‌کند."""

    def __init__(self, max_retries: int = 5) -> None:
        self.max_retries = max_retries
        self._failure_counts: dict[str, int] = {}
        self._loop_detector: dict[str, int] = {}

    def decide(self, task: Task) -> SupervisorDecision:
        """بر اساس وضعیت Task اقدام بعدی را انتخاب می‌کند."""
        if task.status == TaskStatus.SUCCESS and task.result:
            self._failure_counts.pop(task.id, None)
            return SupervisorDecision(SupervisorAction.CONTINUE, "Task با موفقیت تکمیل شد.")

        if task.status == TaskStatus.FAILED:
            failure_count = self._failure_counts.get(task.id, 0) + 1
            self._failure_counts[task.id] = failure_count

            if failure_count >= self.max_retries:
                return SupervisorDecision(
                    SupervisorAction.STOP,
                    f"Task پس از {failure_count} تلاش ناموفق متوقف شد.",
                )

            # تشخیص حلقه تکرار
            error_key = task.error or ""
            loop_count = self._loop_detector.get(f"{task.id}:{error_key}", 0) + 1
            self._loop_detector[f"{task.id}:{error_key}"] = loop_count

            if loop_count >= 3:
                return SupervisorDecision(
                    SupervisorAction.REPLAN,
                    "LOOP_DETECTED: خطا تکراری شناسایی شد؛ نیاز به بازطراحی.",
                )

            return SupervisorDecision(
                SupervisorAction.RETRY,
                f"Task ناموفق بود (تلاش {failure_count}/{self.max_retries}).",
            )

        if task.status == TaskStatus.BLOCKED:
            return SupervisorDecision(SupervisorAction.STOP, "Task به دلیل وابستگی مسدود شده است.")

        if task.status == TaskStatus.CANCELLED:
            return SupervisorDecision(SupervisorAction.SKIP, "Task لغو شده است.")

        return SupervisorDecision(SupervisorAction.STOP, "وضعیت Task برای ادامه معتبر نیست.")

    def reset(self, task_id: str) -> None:
        """شمارنده خطای Task را بازنشانی می‌کند."""
        self._failure_counts.pop(task_id, None)
        keys_to_remove = [k for k in self._loop_detector if k.startswith(f"{task_id}:")]
        for key in keys_to_remove:
            del self._loop_detector[key]

    def stats(self) -> dict[str, int]:
        """آمار خطاها را برمی‌گرداند."""
        return dict(self._failure_counts)
