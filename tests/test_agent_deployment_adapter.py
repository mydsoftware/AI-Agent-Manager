from services.agent_deployment_adapter import AgentDeploymentAdapter, DeploymentContext


def test_adapter_forwards_safe_context_to_executor():
    captured = {}

    def executor(payload):
        captured.update(payload)
        return {"status": "committed"}

    adapter = AgentDeploymentAdapter(executor)
    result = adapter.execute_fix(
        DeploymentContext("p1", "feature/x", "abc123", "https://preview.example.com"),
        {"status": "failed"},
    )
    assert result["status"] == "committed"
    assert captured["project_id"] == "p1"
    assert captured["branch"] == "feature/x"
    assert captured["commit_sha"] == "abc123"
    assert "token" not in captured


def test_adapter_requires_successful_status_for_retry():
    assert AgentDeploymentAdapter.can_retry({"status": "committed"})
    assert not AgentDeploymentAdapter.can_retry({"status": "failed"})
