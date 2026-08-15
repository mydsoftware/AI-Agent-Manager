from manager.loop import AgenticLoop
from manager.task import Task


class Agent:
    def run(self, task):
        return f"done:{task.id}"


class Router:
    def route(self, task):
        return Agent()


def test_agentic_loop_executes_tasks_and_returns_results():
    loop = AgenticLoop(Router())
    result = loop.run([Task(id="task-1", title="demo", description="demo", agent="developer")])
    assert result == ["done:task-1"]
