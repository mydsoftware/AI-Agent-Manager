from manager.context import AgentContext
from manager.context_loop import ContextAwareExecutor
from manager.task import Task


class LoopStub:
    def __init__(self):
        self.calls = []

    def run(self, tasks):
        task = tasks[0]
        self.calls.append(task)
        return [f"done:{task.id}"]


def test_context_aware_executor_resolves_dependencies_and_passes_outputs():
    loop = LoopStub()
    context = AgentContext()
    executor = ContextAwareExecutor(loop, context)

    tasks = [
        Task("design", "طراحی", "طراحی پروژه", "designer"),
        Task("build", "ساخت", "ساخت پروژه", "developer", depends_on=["design"]),
        Task("test", "تست", "تست پروژه", "tester", depends_on=["build"]),
    ]

    results = executor.run(tasks)

    assert results == ["done:design", "done:build", "done:test"]
    assert context.get("design") == "done:design"
    assert context.get("build") == "done:build"
    assert context.get("test") == "done:test"
    assert "done:design" in loop.calls[1].description
    assert "done:build" in loop.calls[2].description


def test_context_aware_executor_detects_unresolvable_dependency():
    executor = ContextAwareExecutor(LoopStub())
    tasks = [Task("a", "A", "A", "developer", depends_on=["missing"])]

    try:
        executor.run(tasks)
        assert False, "expected dependency failure"
    except RuntimeError as error:
        assert "وابستگی قابل حل نیست" in str(error)
