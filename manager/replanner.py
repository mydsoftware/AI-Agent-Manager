from __future__ import annotations

from dataclasses import dataclass

from manager.intention import UserIntent
from manager.multi_plan import MultiAgentPlanner
from manager.supervisor import SupervisorAction, SupervisorDecision
from manager.task import Task


@dataclass
class ReplanResult:
    """نتیجه بازطراحی برنامه اجرای Manager."""

    tasks: list[Task]
    reason: str


class DynamicReplanner:
    """در زمان اجرا، بر اساس تصمیم Supervisor برنامه جدید تولید می‌کند."""

    def __init__(self, planner: MultiAgentPlanner | None = None) -> None:
        self.planner = planner or MultiAgentPlanner()

    def replan(
        self,
        intent: UserIntent,
        completed: list[Task],
        decision: SupervisorDecision,
    ) -> ReplanResult:
        """پس از توقف یا نیاز به تغییر مسیر، برنامه جدید می‌سازد."""
        if decision.action == SupervisorAction.CONTINUE:
            return ReplanResult([], "برنامه فعلی مناسب است و نیازی به بازطراحی ندارد.")

        remaining = self.planner.plan(intent).tasks
        completed_ids = {task.id for task in completed}
        remaining = [task for task in remaining if task.id not in completed_ids]

        if decision.action == SupervisorAction.RETRY:
            reason = "برنامه بر اساس نتیجه ناموفق مرحله قبل بازسازی شد."
        elif decision.action == SupervisorAction.SKIP:
            reason = "برنامه برای عبور از مرحله فعلی بازسازی شد."
        else:
            reason = "Supervisor مسیر فعلی را متوقف کرد؛ برنامه جایگزین بررسی شد."

        return ReplanResult(remaining, reason)
