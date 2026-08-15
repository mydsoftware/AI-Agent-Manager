import threading
import time

from manager.parallel_orchestrator import ParallelAgentOrchestrator
from manager.task import Task


class LoopStub:
    def __init__(self):
        self.started = []
        self.lock = threading.Lock()

    def run(self, tasks):
        task = tasks[0]
        with self.lock:
            self.started.append(task.id)
        time.sleep(0.05)
        return [f"done:{task.id}"]


def test_independent_tasks_run_in_parallel():
    loop = LoopStub()
    orchestrator = ParallelAgentOrchestrator(loop, max_workers=2)
    tasks = [Task("a", "A", "A", "developer"), Task("b", "B", "B", "tester")]

    results = orchestrator.run(tasks)

    assert set(results) == {"done:a", "done:b"}
    assert set(loop.started) == {"a", "b"}
