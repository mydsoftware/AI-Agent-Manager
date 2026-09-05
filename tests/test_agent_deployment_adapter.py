from manager.task_status import TaskStatus
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


def test_adapter_connects_to_real_task_executor():
    class FakeExecutor:
        def __init__(self):
            self.tasks = []

        def run(self, tasks):
            self.tasks.extend(tasks)
            tasks[0].complete("رفع خطای QA انجام شد")
            return [tasks[0].result]

    executor = FakeExecutor()
    adapter = AgentDeploymentAdapter.from_task_executor(executor)
    result = adapter.execute_fix(
        DeploymentContext("project-1", "feature/qa", "sha-1", "https://preview.example.com"),
        {"status": "failed", "error": "button not found"},
    )

    assert result["status"] == "success"
    assert result["project_id"] == "project-1"
    assert len(executor.tasks) == 1
    task = executor.tasks[0]
    assert task.status == TaskStatus.SUCCESS
    assert task.agent == "developer"
    assert task.metadata["project_id"] == "project-1"
    assert task.metadata["branch"] == "feature/qa"
    assert task.metadata["preview_url"] == "https://preview.example.com"
    assert task.metadata["qa"]["error"] == "button not found"
    assert "token" not in task.metadata


def test_real_executor_failure_does_not_allow_retry():
    class FailingExecutor:
        def run(self, tasks):
            tasks[0].fail("executor failed")
            return []

    adapter = AgentDeploymentAdapter.from_task_executor(FailingExecutor())
    result = adapter.execute_fix(
        DeploymentContext("project-2", "feature/qa", "sha-2"),
        {"status": "failed"},
    )

    assert result["status"] == "failed"
    assert not adapter.can_retry(result)
