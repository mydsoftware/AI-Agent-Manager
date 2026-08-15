from manager.orchestrator import ManagerOrchestrator
from manager.task import Task
from manager.report import ManagerReport


class ExecutorStub:
    def __init__(self):
        self.loop = None
        self.calls = []

    def run(self, tasks):
        self.calls.extend(tasks)
        return tasks


def test_runtime_orchestrator_accepts_explicit_agent_override():
    executor = ExecutorStub()
    report = ManagerOrchestrator().execute("برای گیتهاب کار کن", executor, agent="github")
    assert isinstance(report, ManagerReport)
    assert executor.calls
    assert all(task.agent == "github" for task in executor.calls)
