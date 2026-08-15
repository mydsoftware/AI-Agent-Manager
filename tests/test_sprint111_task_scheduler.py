from manager.task_scheduler import TaskScheduler
from manager.task import Task


class LoopStub:
    def run(self, tasks):
        return [f"done:{tasks[0].id}"]


def test_scheduler_respects_dependencies_and_priority():
    scheduler = TaskScheduler(LoopStub())
    high = Task("high", "High", "high", "developer")
    high.priority = 10
    low = Task("low", "Low", "low", "developer")
    low.priority = 1
    dependent = Task("dependent", "Dependent", "dependent", "developer", depends_on=["high"])

    assert scheduler.run([low, dependent, high]) == ["done:high", "done:low", "done:dependent"]
