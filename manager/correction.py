from __future__ import annotations

from dataclasses import replace

from manager.feedback import FeedbackDecision
from manager.task import Task


class CorrectionFactory:
    """برای نتیجه ردشده، Task اصلاحی ایجاد می‌کند."""

    def create(self, task: Task, decision: FeedbackDecision, attempt: int) -> Task:
        """یک Task اصلاحی وابسته به Task قبلی می‌سازد."""
        return Task(
            id=f"{task.id}-correction-{attempt}",
            title=f"اصلاح {task.title}",
            description=(
                f"نتیجه مرحله قبل پذیرفته نشد.\n"
                f"دلیل: {decision.reason}\n"
                f"نتیجه قبلی: {task.result}\n"
                "وظیفه را اصلاح و دوباره اجرا کن."
            ),
            agent=task.agent,
            depends_on=[],
        )
