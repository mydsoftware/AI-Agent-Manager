from __future__ import annotations

from dataclasses import dataclass

from manager.task import Task
from manager.task_status import TaskStatus


@dataclass
class FeedbackDecision:
    """تصمیم Manager پس از بررسی نتیجه یک Task."""

    accepted: bool
    reason: str
    retry: bool = False


class FeedbackEngine:
    """نتیجه اجرای Agent را بررسی و درباره ادامه مسیر تصمیم می‌گیرد."""

    def evaluate(self, task: Task) -> FeedbackDecision:
        """موفقیت Task و وجود نتیجه قابل استفاده را بررسی می‌کند."""
        if task.status != TaskStatus.SUCCESS:
            return FeedbackDecision(False, "وظیفه با موفقیت اجرا نشده است.", True)
        if task.result is None or not str(task.result).strip():
            return FeedbackDecision(False, "Agent خروجی قابل استفاده تولید نکرده است.", True)
        return FeedbackDecision(True, "نتیجه Agent قابل استفاده است.")


class FeedbackLoop:
    """اجرای Task و ارزیابی نتیجه را تا سقف تلاش مجاز تکرار می‌کند."""

    def __init__(self, evaluator: FeedbackEngine | None = None, max_attempts: int = 2) -> None:
        self.evaluator = evaluator or FeedbackEngine()
        self.max_attempts = max_attempts

    def evaluate(self, task: Task) -> FeedbackDecision:
        """نتیجه موجود را ارزیابی می‌کند."""
        return self.evaluator.evaluate(task)
