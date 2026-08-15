from manager.orchestration import AgentOrchestrator
from manager.task import Task


class LoopStub:
    def run(self, tasks):
        return [f"done:{tasks[0].id}"]


def test_orchestrator_runs_dependency_chain():
    orchestrator = AgentOrchestrator(LoopStub())
    tasks = [
        Task("deploy", "استقرار", "استقرار", "developer", depends_on=["build"]),
        Task("build", "ساخت", "ساخت", "developer"),
    ]
    assert orchestrator.run(tasks) == ["done:build", "done:deploy"]
    assert orchestrator.context.get("deploy") == "done:deploy"
