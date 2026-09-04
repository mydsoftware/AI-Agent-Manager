"""ارکستریتور حلقه استقرار خودکار از Preview تا QA و تحلیل نتیجه."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable


class DeploymentState(str, Enum):
    CI_WAITING = "ci_waiting"
    CI_PASSED = "ci_passed"
    CI_FAILED = "ci_failed"
    PREVIEW_DEPLOYING = "preview_deploying"
    PREVIEW_READY = "preview_ready"
    BROWSER_QA_RUNNING = "browser_qa_running"
    BROWSER_QA_PASSED = "browser_qa_passed"
    BROWSER_QA_FAILED = "browser_qa_failed"
    ANALYZING = "analyzing"
    FIXING = "fixing"
    COMMITTING = "committing"
    MAX_RETRIES = "max_retries"
    PRODUCTION_PENDING_APPROVAL = "production_pending_approval"
    PRODUCTION_DEPLOYING = "production_deploying"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class DeploymentLoopResult:
    state: DeploymentState
    attempts: int
    history: list[str] = field(default_factory=list)
    last_result: dict[str, Any] = field(default_factory=dict)


class AutonomousDeploymentLoop:
    """ماشین حالت محدود برای اجرای Preview→QA→Fix→Commit→تکرار."""

    def __init__(self, max_attempts: int = 3) -> None:
        if max_attempts < 1:
            raise ValueError("max_attempts باید حداقل ۱ باشد.")
        self.max_attempts = max_attempts

    def run(
        self,
        ci_passed: bool,
        deploy_preview: Callable[[], dict[str, Any]],
        browser_qa: Callable[[str], dict[str, Any]],
        analyze_failure: Callable[[dict[str, Any]], bool] | None = None,
        fix_and_commit: Callable[[dict[str, Any]], bool] | None = None,
    ) -> DeploymentLoopResult:
        history = [DeploymentState.CI_WAITING.value]
        if not ci_passed:
            history.append(DeploymentState.CI_FAILED.value)
            return DeploymentLoopResult(DeploymentState.CI_FAILED, 0, history)

        history.append(DeploymentState.CI_PASSED.value)
        for attempt in range(1, self.max_attempts + 1):
            history.append(DeploymentState.PREVIEW_DEPLOYING.value)
            preview = deploy_preview()
            preview_url = str(preview.get("url", "")).strip()
            if not preview_url:
                history.append(DeploymentState.FAILED.value)
                return DeploymentLoopResult(DeploymentState.FAILED, attempt, history, preview)

            history.append(DeploymentState.PREVIEW_READY.value)
            history.append(DeploymentState.BROWSER_QA_RUNNING.value)
            qa = browser_qa(preview_url)
            if qa.get("status") == "passed":
                history.append(DeploymentState.BROWSER_QA_PASSED.value)
                history.append(DeploymentState.PRODUCTION_PENDING_APPROVAL.value)
                return DeploymentLoopResult(DeploymentState.PRODUCTION_PENDING_APPROVAL, attempt, history, qa)

            history.append(DeploymentState.BROWSER_QA_FAILED.value)
            if analyze_failure is None or fix_and_commit is None:
                history.append(DeploymentState.FAILED.value)
                return DeploymentLoopResult(DeploymentState.FAILED, attempt, history, qa)

            history.append(DeploymentState.ANALYZING.value)
            if not analyze_failure(qa):
                history.append(DeploymentState.FAILED.value)
                return DeploymentLoopResult(DeploymentState.FAILED, attempt, history, qa)

            if attempt == self.max_attempts:
                history.append(DeploymentState.MAX_RETRIES.value)
                return DeploymentLoopResult(DeploymentState.MAX_RETRIES, attempt, history, qa)

            history.append(DeploymentState.FIXING.value)
            if not fix_and_commit(qa):
                history.append(DeploymentState.FAILED.value)
                return DeploymentLoopResult(DeploymentState.FAILED, attempt, history, qa)
            history.append(DeploymentState.COMMITTING.value)

        return DeploymentLoopResult(DeploymentState.FAILED, self.max_attempts, history)
