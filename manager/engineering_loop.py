from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable

from manager.failure_analyzer import FailureAnalysis, FailureAnalyzer


class EngineeringState(str, Enum):
    PLAN = "plan"
    BRANCH = "branch"
    CHANGE = "change"
    VERIFY = "verify"
    ANALYZE = "analyze"
    REPAIR = "repair"
    PR = "pr"
    DONE = "done"
    FAILED = "failed"


@dataclass
class EngineeringResult:
    state: EngineeringState
    attempts: int
    ci_status: str | None = None
    error: str | None = None
    failure_analysis: FailureAnalysis | None = None


class EngineeringLoop:
    """چرخه مهندسی با تحلیل شکست قبل از Repair."""

    def __init__(self, max_attempts: int = 3, failure_analyzer: FailureAnalyzer | None = None) -> None:
        if max_attempts < 1:
            raise ValueError("max_attempts باید حداقل ۱ باشد.")
        self.max_attempts = max_attempts
        self.failure_analyzer = failure_analyzer or FailureAnalyzer()

    def run(
        self,
        create_branch: Callable[[], object],
        apply_change: Callable[[], object],
        check_ci: Callable[[], str],
        repair: Callable[[FailureAnalysis], object],
        create_pr: Callable[[], object],
        get_ci_log: Callable[[], str] | None = None,
    ) -> EngineeringResult:
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

            log = get_ci_log() if get_ci_log else status
            analysis = self.failure_analyzer.analyze(log, status)
            if attempt == self.max_attempts:
                return EngineeringResult(EngineeringState.FAILED, attempt, status, "تست پس از حداکثر تلاش‌ها موفق نشد.", analysis)

            try:
                repair(analysis)
            except Exception as error:
                return EngineeringResult(EngineeringState.FAILED, attempt, status, str(error), analysis)

        return EngineeringResult(EngineeringState.FAILED, self.max_attempts, error="چرخه بدون نتیجه پایان یافت.")
