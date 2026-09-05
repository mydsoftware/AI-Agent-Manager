"""اتصال عملی CI/Preview/Browser QA به حلقه خودکار استقرار."""

from __future__ import annotations

from typing import Any, Callable

from manager.task import Task
from services.agent_deployment_adapter import AgentDeploymentAdapter, DeploymentContext
from services.autonomous_deployment_loop import AutonomousDeploymentLoop, DeploymentLoopResult, DeploymentState
from services.browser_qa import BrowserQA
from services.ci_monitor import CIMonitor
from services.vercel_deployment import VercelDeploymentService


class DeploymentOrchestrator:
    """اجرای پروژه‌محور و محدودشده‌ی CI → Fix → Preview → QA."""

    def __init__(
        self,
        executor: Any,
        vercel: VercelDeploymentService,
        browser_qa: BrowserQA,
        max_attempts: int = 3,
        ci_monitor: CIMonitor | None = None,
        max_ci_polls: int = 5,
    ) -> None:
        if max_ci_polls < 1:
            raise ValueError("max_ci_polls باید حداقل ۱ باشد.")
        self.executor = executor
        self.vercel = vercel
        self.browser_qa = browser_qa
        self.ci_monitor = ci_monitor
        self.max_ci_polls = max_ci_polls
        self.loop = AutonomousDeploymentLoop(max_attempts=max_attempts)

    def run(
        self,
        context: DeploymentContext,
        ci_passed: bool,
        deploy_preview: Callable[[], dict[str, Any]],
        owner: str = "",
        repository: str = "",
    ) -> DeploymentLoopResult:
        """Loop را اجرا می‌کند و در صورت تنظیم CI Monitor، خطای CI را نیز خودکار رفع می‌کند."""
        adapter = AgentDeploymentAdapter(self._execute_fix_task)
        ci_failure: dict[str, Any] = {}
        history: list[str] = []

        if self.ci_monitor is not None and owner and repository:
            ci_result = self._wait_for_ci(owner, repository, context.branch)
            if ci_result["status"] == "pending":
                return DeploymentLoopResult(
                    DeploymentState.CI_WAITING,
                    0,
                    [DeploymentState.CI_WAITING.value],
                    ci_result,
                )
            if ci_result["status"] == "failed":
                ci_failure = ci_result.get("failure", {})
                ci_passed = False
            elif ci_result["status"] == "passed":
                ci_passed = True

        def analyze(result: dict[str, Any]) -> bool:
            return result.get("status") == "failed"

        def fix_and_commit(result: dict[str, Any]) -> bool:
            payload = dict(result)
            if ci_failure:
                payload["ci_failure"] = ci_failure
            fix_result = adapter.execute_fix(context, payload)
            return adapter.can_retry(fix_result)

        if not ci_passed:
            if not ci_failure or self.ci_monitor is None or not owner or not repository:
                return DeploymentLoopResult(
                    DeploymentState.CI_FAILED,
                    0,
                    [DeploymentState.CI_WAITING.value, DeploymentState.CI_FAILED.value],
                    {"status": "failed", "failure": ci_failure},
                )
            history.extend([DeploymentState.CI_WAITING.value, DeploymentState.CI_FAILED.value])
            if not fix_and_commit({"status": "failed", "source": "github_actions", "failure": ci_failure}):
                history.append(DeploymentState.FAILED.value)
                return DeploymentLoopResult(DeploymentState.FAILED, 0, history, ci_failure)
            history.append(DeploymentState.FIXING.value)
            history.append(DeploymentState.COMMITTING.value)
            ci_after_fix = self._wait_for_ci(owner, repository, context.branch)
            history.append(DeploymentState.CI_WAITING.value)
            if ci_after_fix["status"] != "passed":
                history.append(
                    DeploymentState.MAX_RETRIES.value
                    if ci_after_fix["status"] == "failed"
                    else DeploymentState.CI_WAITING.value
                )
                return DeploymentLoopResult(
                    DeploymentState.MAX_RETRIES if ci_after_fix["status"] == "failed" else DeploymentState.CI_WAITING,
                    1,
                    history,
                    ci_after_fix,
                )
            ci_passed = True

        result = self.loop.run(
            ci_passed=ci_passed,
            deploy_preview=deploy_preview,
            browser_qa=self.browser_qa.run_smoke,
            analyze_failure=analyze,
            fix_and_commit=fix_and_commit,
        )
        if history:
            result.history = history + result.history[1:]
        return result

    def _wait_for_ci(self, owner: str, repository: str, branch: str) -> dict[str, Any]:
        """CI را با سقف polling می‌خواند تا Agent در انتظار بی‌نهایت نماند."""
        assert self.ci_monitor is not None
        latest: dict[str, Any] = {"status": "pending", "branch": branch}
        for _ in range(self.max_ci_polls):
            latest = self.ci_monitor.latest(owner, repository, branch)
            if latest.get("status") in {"passed", "failed", "not_found"}:
                return latest
        return latest

    def _execute_fix_task(self, payload: dict[str, Any]) -> dict[str, Any]:
        """درخواست Fix را فقط از مسیر TaskExecutor واقعی عبور می‌دهد."""
        task = Task(
            title="رفع خطای CI/Browser QA",
            description=(
                "خطای CI یا Browser QA را در Branch پروژه تحلیل و رفع کن؛ "
                "هرگز Production را مستقیم تغییر نده. "
                f"project={payload['project_id']} branch={payload['branch']} "
                f"commit={payload['commit_sha']} preview={payload.get('preview_url', '')} "
                f"qa={payload.get('qa', {})} ci={payload.get('ci_failure', {})}"
            ),
            agent="developer",
            metadata={
                "deployment_action": "fix_ci_or_browser_qa_failure",
                "project_id": payload["project_id"],
                "branch": payload["branch"],
                "commit_sha": payload["commit_sha"],
                "ci_failure": payload.get("ci_failure", {}),
            },
            max_attempts=1,
        )
        try:
            results = self.executor.run([task])
            if task.status.value != "success":
                return {"status": "failed", "error": task.error or "Fix task failed"}
            return {
                "status": "committed" if results else "fixed",
                "task_id": task.id,
                "result": task.result,
            }
        except Exception as error:
            return {"status": "failed", "error": str(error), "task_id": task.id}
