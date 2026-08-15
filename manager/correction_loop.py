from __future__ import annotations

from manager.context import AgentContext
from manager.correction import CorrectionFactory
from manager.feedback import FeedbackEngine
from manager.loop import AgenticLoop
from manager.task import Task
from manager.task_status import TaskStatus


class CorrectionLoop:
    """در صورت رد نتیجه، Task اصلاحی می‌سازد و Context را حفظ می‌کند."""

    def __init__(self, loop: AgenticLoop, context: AgentContext | None = None, max_attempts: int = 2) -> None:
        self.loop = loop
        self.context = context or AgentContext()
        self.feedback = FeedbackEngine()
        self.corrections = CorrectionFactory()
        self.max_attempts = max_attempts

    def _apply_context(self, task: Task) -> None:
        """خروجی وابستگی‌ها را قبل از اجرای Task وارد توضیحات می‌کند."""
        if not task.depends_on:
            return
        inputs = {dependency: self.context.get(dependency) for dependency in task.depends_on}
        task.description = f"{task.description}\n\nخروجی مراحل قبلی:\n{inputs}"

    def run(self, task: Task) -> Task:
        """Task را اجرا، ارزیابی و در صورت نیاز با همان Context اصلاح می‌کند."""
        current = task
        for attempt in range(1, self.max_attempts + 1):
            self._apply_context(current)
            try:
                current.status = TaskStatus.RUNNING
                current.result = self.loop.run([current])[0]
                current.status = TaskStatus.SUCCESS
                current.error = None
            except Exception as error:
                current.status = TaskStatus.FAILED
                current.error = str(error)

            decision = self.feedback.evaluate(current)
            if decision.accepted:
                self.context.set(task.id, current.result)
                self.context.set(current.id, current.result)
                return current

            if attempt == self.max_attempts:
                current.error = decision.reason
                return current

            corrected = self.corrections.create(current, decision, attempt)
            corrected.depends_on = list(task.depends_on)
            current = corrected

        return current
