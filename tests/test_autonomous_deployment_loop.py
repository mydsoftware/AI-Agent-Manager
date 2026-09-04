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
