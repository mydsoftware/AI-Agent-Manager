from manager.context import AgentContext
from manager.context_agent import ContextAgentRunner
from manager.feedback import FeedbackEngine
from manager.task import Task
from manager.task_status import TaskStatus


class LoopStub:
    def __init__(self):
        self.calls = []

    def run(self, tasks):
        self.calls.append((tasks[0].id, tasks[0].description))
        return [f"done:{tasks[0].id}"]


class FeedbackStub:
    def evaluate(self, task):
        return type("Decision", (), {"accepted": True, "reason": "تأیید شد"})()


def test_context_agent_runner_forwards_previous_output_and_marks_success():
    loop = LoopStub()
    context = AgentContext()
    runner = ContextAgentRunner(loop, context, FeedbackStub())

    tasks = [
        Task("deploy", "استقرار", "استقرار پروژه", "developer", depends_on=["build"]),
        Task("build", "ساخت", "ساخت پروژه", "developer"),
    ]

    results = runner.run(tasks)

    assert results == ["done:build", "done:deploy"]
    assert context.get("build") == "done:build"
    assert context.get("deploy") == "done:deploy"
    assert tasks[0].status == TaskStatus.SUCCESS
    assert "done:build" in loop.calls[1][1]
