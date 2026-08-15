from manager.context import AgentContext
from manager.context_loop import ContextAwareExecutor
from manager.task import Task


class LoopStub:
    def __init__(self):
        self.calls = []

    def run(self, tasks):
        task = tasks[0]
        self.calls.append(task.id)
        return [f"done:{task.id}"]


def test_orchestration_runs_dependency_chain_deterministically():
    loop = LoopStub()
    context = AgentContext()
    executor = ContextAwareExecutor(loop, context)

    tasks = [
        Task("deploy", "استقرار", "استقرار", "dev", depends_on=["test"]),
        Task("test", "تست", "تست", "qa", depends_on=["build"]),
        Task("build", "ساخت", "ساخت", "dev"),
    ]

    results = executor.run(tasks)

    assert loop.calls == ["build", "test", "deploy"]
    assert results == ["done:build", "done:test", "done:deploy"]
