from manager.executor import TaskExecutor
from manager.task import Task
from manager.task_status import TaskStatus
from services.workflow_store import WorkflowStore


class CountingLoop:
    def __init__(self):
        self.calls = 0

    def run(self, tasks):
        self.calls += 1
        return [f"result-{self.calls}"]


def test_executor_does_not_rerun_successful_tasks():
    loop = CountingLoop()
    first = Task(id="first", title="first", agent="developer", status=TaskStatus.SUCCESS, result="already done")
    second = Task(id="second", title="second", agent="developer", depends_on=["first"])

    results = TaskExecutor(loop).run([first, second])

    assert results == ["result-1"]
    assert loop.calls == 1
    assert first.result == "already done"
    assert second.status == TaskStatus.SUCCESS


def test_workflow_store_persists_and_transitions_state(tmp_path):
    store = WorkflowStore(str(tmp_path / "workflow.db"))
    plan = {"name": "resume-test", "tasks": [{"id": "task-1", "status": "success"}]}

    saved = store.save("project-1", plan, state="running", attempts=1)
    assert saved["state"] == "running"
    assert saved["attempts"] == 1

    transitioned = store.transition("project-1", "browser_qa", attempts=2, last_error=None)
    assert transitioned is not None
    assert transitioned["state"] == "browser_qa"
    assert transitioned["attempts"] == 2
    assert transitioned["workflow"] == plan
