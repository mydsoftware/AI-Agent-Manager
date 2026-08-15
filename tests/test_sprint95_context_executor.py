import pytest

from manager.context_loop import ContextAwareExecutor
from manager.task import Task


class LoopStub:
    def __init__(self):
        self.calls = []

    def run(self, tasks):
        self.calls.append([task.id for task in tasks])
        return [f"خروجی {tasks[0].id}"]


def test_executor_rejects_missing_dependency():
    loop = LoopStub()
    executor = ContextAwareExecutor(loop)
    tasks = [Task(id="build", description="ساخت", depends_on=["missing"])]

    with pytest.raises(RuntimeError, match="وابستگی‌های تعریف‌نشده"):
        executor.run(tasks)


def test_executor_executes_dependency_chain_in_order():
    loop = LoopStub()
    executor = ContextAwareExecutor(loop)
    tasks = [
        Task(id="deploy", description="استقرار", depends_on=["build"]),
        Task(id="build", description="ساخت", depends_on=[]),
    ]

    results = executor.run(tasks)

    assert loop.calls == [["build"], ["deploy"]]
    assert results == ["خروجی build", "خروجی deploy"]
    assert executor.context.get("build") == "خروجی build"
    assert executor.context.get("deploy") == "خروجی deploy"
