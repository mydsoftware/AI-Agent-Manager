from manager.approval_policy import sensitive_tasks
from manager.task import Task


def test_detects_github_and_deploy_tasks():
    tasks = [
        Task(id="a", title="Build UI", agent="developer"),
        Task(id="b", title="Deploy production", agent="developer"),
        Task(id="c", title="Publish repository", agent="github"),
    ]
    assert [task.id for task in sensitive_tasks(tasks)] == ["b", "c"]


def test_normal_task_does_not_require_approval():
    tasks = [Task(id="a", title="Write unit tests", description="Run local tests", agent="qa")]
    assert sensitive_tasks(tasks) == []
