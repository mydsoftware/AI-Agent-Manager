from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable


class EngineeringState(str, Enum):
    """وضعیت‌های چرخه مهندسی خودکار."""

    PLAN = "plan"
    BRANCH = "branch"
    CHANGE = "change"
    VERIFY = "verify"
    REPAIR = "repair"
    PR = "pr"
    DONE = "done"
    FAILED = "failed"


@dataclass
class EngineeringResult:
    """نتیجه اجرای چرخه مهندسی."""

    state: EngineeringState
    attempts: int
    ci_status: str | None = None
    error: str | None = None


class EngineeringLoop:
    """ماشین حالت محدود برای اجرای چرخه تغییر، تست، اصلاح و PR."""

    def __init__(self, max_attempts: int = 3) -> None:
        if max_attempts < 1:
            raise ValueError("max_attempts باید حداقل ۱ باشد.")
        self.max_attempts = max_attempts

    def run(
        self,
        create_branch: Callable[[], object],
        apply_change: Callable[[], object],
        check_ci: Callable[[], str],
        repair: Callable[[str], object],
        create_pr: Callable[[], object],
    ) -> EngineeringResult:
        """چرخه را تا موفقیت یا رسیدن به سقف تلاش‌ها اجرا می‌کند."""
        try:
            create_branch()
            apply_change()
        except Exception as error:
            return EngineeringResult(EngineeringState.FAILED, 0, error=str(error))

        for attempt in range(1, self.max_attempts + 1):
            try:
                status = check_ci().lower()
            except Exception as error:
                return EngineeringResult(EngineeringState.FAILED, attempt, error=str(error))

            if status in {"success", "passed", "pass", "completed"}:
                try:
                    create_pr()
                except Exception as error:
                    return EngineeringResult(EngineeringState.FAILED, attempt, status, str(error))
                return EngineeringResult(EngineeringState.DONE, attempt, status)

            if status in {"queued", "in_progress", "pending", "waiting"}:
                return EngineeringResult(EngineeringState.VERIFY, attempt, status)

            if attempt == self.max_attempts:
                return EngineeringResult(EngineeringState.FAILED, attempt, status, "تست پس از حداکثر تلاش‌ها موفق نشد.")

            try:
                repair(status)
            except Exception as error:
                return EngineeringResult(EngineeringState.FAILED, attempt, status, str(error))

        return EngineeringResult(EngineeringState.FAILED, self.max_attempts, error="چرخه بدون نتیجه پایان یافت.")
