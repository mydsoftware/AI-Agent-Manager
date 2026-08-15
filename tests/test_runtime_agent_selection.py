from manager.orchestrator import ManagerOrchestrator
from manager.report import ManagerReport
from manager.task_status import TaskStatus


class ExecutorStub:
    class Loop:
        def run(self, tasks):
            return [f"done:{task.id}" for task in tasks]

    loop = Loop()


def test_runtime_orchestrator_accepts_explicit_agent_override():
    executor = ExecutorStub()
    report = ManagerOrchestrator().execute("برای گیتهاب کار کن", executor, agent="github")
    assert isinstance(report, ManagerReport)
    assert report.tasks
    assert all(task.agent == "github" for task in report.tasks)
    assert report.status == TaskStatus.SUCCESS
