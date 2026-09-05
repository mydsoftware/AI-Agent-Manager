"""اتصال عملی Loop استقرار به CI/Preview/Browser QA و Executor."""

from __future__ import annotations

from typing import Any

from manager.task import Task
from services.agent_deployment_adapter import AgentDeploymentAdapter, DeploymentContext
from services.autonomous_deployment_loop import AutonomousDeploymentLoop, DeploymentLoopResult
from services.browser_qa import BrowserQA
from services.vercel_deployment import VercelDeploymentService


class DeploymentOrchestrator:
    """یک اجرای پروژه‌محور و امن از حلقه توسعه تا QA."""

    def __init__(
        self,
        executor: Any,
        vercel: VercelDeploymentService,
        browser_qa: BrowserQA,
        max_attempts: int = 3,
    ) -> None:
        self.executor = executor
        self.vercel = vercel
        self.browser_qa = browser_qa
        self.loop = AutonomousDeploymentLoop(max_attempts=max_attempts)

    def run(
        self,
        context: DeploymentContext,
        ci_passed: bool,
        deploy_preview: Any,
    ) -> DeploymentLoopResult:
        adapter = AgentDeploymentAdapter(self._execute_fix_task)

        def analyze(qa: dict[str, Any]) -> bool:
            return qa.get("status") == "failed"

        def fix_and_commit(qa: dict[str, Any]) -> bool:
            result = adapter.execute_fix(context, qa)
            return adapter.can_retry(result)

        return self.loop.run(
            ci_passed=ci_passed,
            deploy_preview=deploy_preview,
            browser_qa=self.browser_qa.run_smoke,
            analyze_failure=analyze,
            fix_and_commit=fix_and_commit,
        )

    def _execute_fix_task(self, payload: dict[str, Any]) -> dict[str, Any]:
        """درخواست Fix را از مسیر TaskExecutor واقعی عبور می‌دهد."""
        task = Task(
            title="رفع خطای Browser QA",
            description=(
                "رفع خطای QA در Preview پروژه بدون استقرار Production. "
                f"project={payload['project_id']} branch={payload['branch']} "
                f"commit={payload['commit_sha']} preview={payload['preview_url']} "
                f"qa={payload['qa']}"
            ),
            agent="developer",
            metadata={
                "deployment_action": "fix_browser_qa_failure",
                "project_id": payload["project_id"],
                "branch": payload["branch"],
                "commit_sha": payload["commit_sha"],
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
