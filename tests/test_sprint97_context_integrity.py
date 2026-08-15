from manager.context import AgentContext
from manager.context_loop import ContextAwareExecutor
from manager.task import Task


class LoopStub:
    def run(self, tasks):
        return [f"done:{tasks[0].id}"]


def test_context_is_isolated_per_executor():
    first = AgentContext()
    second = AgentContext()

    ContextAwareExecutor(LoopStub(), first).run([
        Task("build", "ساخت", "ساخت", "developer")
    ])

    assert first.get("build") == "done:build"
    assert second.get("build") is None


def test_dependency_output_is_forwarded_to_next_agent():
    context = AgentContext()
    executor = ContextAwareExecutor(LoopStub(), context)

    executor.run([
        Task("test", "تست", "اجرای تست", "tester", depends_on=["build"]),
        Task("build", "ساخت", "ساخت پروژه", "developer"),
    ])

    assert context.get("build") == "done:build"
    assert context.get("test") == "done:test"
