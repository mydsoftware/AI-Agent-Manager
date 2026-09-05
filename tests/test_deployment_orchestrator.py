from services.agent_deployment_adapter import DeploymentContext
from services.browser_qa import BrowserQA
from services.deployment_orchestrator import DeploymentOrchestrator
from services.vercel_deployment import VercelDeploymentService, VercelConfig


class FakeExecutor:
    def __init__(self):
        self.tasks = []

    def run(self, tasks):
        self.tasks.extend(tasks)
        tasks[0].complete("fix applied")
        return ["fix applied"]


class FakeQA(BrowserQA):
    def __init__(self):
        self.calls = 0

    def run_smoke(self, url):
        self.calls += 1
        return {"url": url, "status": "failed" if self.calls == 1 else "passed"}


def test_orchestrator_routes_qa_fix_through_executor():
    executor = FakeExecutor()
    qa = FakeQA()
    service = VercelDeploymentService(VercelConfig(token=""))
    orchestrator = DeploymentOrchestrator(executor, service, qa, max_attempts=3)

    calls = {"deploy": 0}

    def deploy_preview():
        calls["deploy"] += 1
        return {"url": f"https://preview-{calls['deploy']}.example.com"}

    result = orchestrator.run(
        DeploymentContext("project-1", "feature/fix", "sha-1"),
        ci_passed=True,
        deploy_preview=deploy_preview,
    )

    assert result.state.value == "production_pending_approval"
    assert len(executor.tasks) == 1
    assert executor.tasks[0].metadata["project_id"] == "project-1"
    assert executor.tasks[0].metadata["branch"] == "feature/fix"


def test_orchestrator_does_not_bypass_failed_executor():
    class FailingExecutor:
        def run(self, tasks):
            tasks[0].fail("agent failed")
            return []

    qa = FakeQA()
    orchestrator = DeploymentOrchestrator(
        FailingExecutor(),
        VercelDeploymentService(VercelConfig(token="")),
        qa,
        max_attempts=3,
    )
    result = orchestrator.run(
        DeploymentContext("project-2", "feature/fix", "sha-2"),
        True,
        lambda: {"url": "https://preview.example.com"},
    )
    assert result.state.value == "failed"
