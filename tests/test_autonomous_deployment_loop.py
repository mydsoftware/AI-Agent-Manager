from services.agent_deployment_adapter import AgentDeploymentAdapter, DeploymentContext
from services.autonomous_deployment_loop import AutonomousDeploymentLoop, DeploymentState


def test_ci_failure_stops_before_preview():
    called = []
    result = AutonomousDeploymentLoop().run(False, lambda: called.append(1), lambda _: {})
    assert result.state is DeploymentState.CI_FAILED
    assert called == []


def test_success_stops_at_production_approval():
    result = AutonomousDeploymentLoop().run(
        True,
        lambda: {"url": "https://preview.example.com"},
        lambda url: {"url": url, "status": "passed"},
    )
    assert result.state is DeploymentState.PRODUCTION_PENDING_APPROVAL
    assert DeploymentState.BROWSER_QA_PASSED.value in result.history


def test_failed_qa_can_fix_and_retry():
    calls = {"deploy": 0, "fix": 0}

    def deploy():
        calls["deploy"] += 1
        return {"url": f"https://preview-{calls['deploy']}.example.com"}

    def qa(_):
        return {"status": "failed" if calls["deploy"] == 1 else "passed"}

    def analyze(_):
        return True

    def fix(_):
        calls["fix"] += 1
        return True

    result = AutonomousDeploymentLoop(max_attempts=3).run(True, deploy, qa, analyze, fix)
    assert result.state is DeploymentState.PRODUCTION_PENDING_APPROVAL
    assert calls["fix"] == 1


def test_max_retries_is_terminal():
    result = AutonomousDeploymentLoop(max_attempts=2).run(
        True,
        lambda: {"url": "https://preview.example.com"},
        lambda _: {"status": "failed"},
        lambda _: True,
        lambda _: True,
    )
    assert result.state is DeploymentState.MAX_RETRIES
    assert result.attempts == 2


def test_loop_uses_real_executor_adapter_for_qa_fix():
    calls = []

    class FakeExecutor:
        def run(self, tasks):
            calls.append(tasks[0])
            tasks[0].complete("fixed")
            return ["fixed"]

    adapter = AgentDeploymentAdapter.from_task_executor(FakeExecutor())
    deployments = {"count": 0}

    def deploy():
        deployments["count"] += 1
        return {"url": f"https://preview-{deployments['count']}.example.com"}

    def qa(_url):
        return {"status": "failed" if deployments["count"] == 1 else "passed"}

    result = AutonomousDeploymentLoop(max_attempts=2).run(
        True,
        deploy,
        qa,
        deployment_adapter=adapter,
        deployment_context=DeploymentContext("p1", "feature/qa", "sha1"),
    )

    assert result.state is DeploymentState.PRODUCTION_PENDING_APPROVAL
    assert len(calls) == 1
    assert calls[0].metadata["project_id"] == "p1"
    assert calls[0].metadata["branch"] == "feature/qa"
