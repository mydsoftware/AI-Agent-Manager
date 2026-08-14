from __future__ import annotations

from manager.correction import CorrectionFactory
from manager.feedback import FeedbackEngine
from manager.loop import AgenticLoop
from manager.task import Task
from manager.task_status import TaskStatus


class CorrectionLoop:
    """در صورت رد نتیجه، Task اصلاحی می‌سازد و دوباره ارزیابی می‌کند."""

    def __init__(self, loop: AgenticLoop, max_attempts: int = 2) -> None:
        self.loop = loop
        self.feedback = FeedbackEngine()
        self.corrections = CorrectionFactory()
        self.max_attempts = max_attempts

    def run(self, task: Task) -> Task:
        """یک Task را اجرا و در صورت نیاز اصلاح و تکرار می‌کند."""
        current = task
        for attempt in range(1, self.max_attempts + 1):
            try:
                current.status = TaskStatus.RUNNING
                current.result = self.loop.run([current])[0]
                current.status = TaskStatus.SUCCESS
            except Exception as error:
                current.status = TaskStatus.FAILED
                current.error = str(error)

            decision = self.feedback.evaluate(current)
            if decision.accepted:
                return current

            if attempt == self.max_attempts:
                current.error = decision.reason
                return current

            current = self.corrections.create(current, decision, attempt)

        return current
