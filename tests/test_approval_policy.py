from manager.approval_policy import approval_fingerprint, sensitive_tasks
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


def test_approval_fingerprint_is_stable_for_same_operation():
    tasks = [Task(id="b", title="Deploy production", description="Deploy preview", agent="developer")]
    first = approval_fingerprint("project-1", "workflow.sensitive-run", tasks)
    second = approval_fingerprint("project-1", "workflow.sensitive-run", list(reversed(tasks)))
    assert first == second
    assert len(first) == 64


def test_approval_fingerprint_changes_when_sensitive_task_changes():
    original = [Task(id="b", title="Deploy production", description="Deploy preview", agent="developer")]
    changed = [Task(id="b", title="Deploy production", description="Deploy production", agent="developer")]
    assert approval_fingerprint("project-1", "workflow.sensitive-run", original) != approval_fingerprint("project-1", "workflow.sensitive-run", changed)


def test_approval_fingerprint_is_bound_to_project_and_action():
    tasks = [Task(id="b", title="Deploy production", agent="developer")]
    fingerprint = approval_fingerprint("project-1", "workflow.sensitive-run", tasks)
    assert fingerprint != approval_fingerprint("project-2", "workflow.sensitive-run", tasks)
    assert fingerprint != approval_fingerprint("project-1", "other-action", tasks)
