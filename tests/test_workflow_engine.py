from __future__ import annotations

from api.agent_team_api import AgentTeamAPI
from api.http import create_app
from manager.task import Task
from manager.task_status import TaskStatus
from manager.workflow_engine import WorkflowEngine
from runtime import ManagerRuntime
from services.project_store import ProjectStore


def build_runtime(tmp_path):
    return ManagerRuntime(
        database_path=str(tmp_path / "manager.db"),
        registry_path=str(tmp_path / "agents.json"),
    )


def test_workflow_plan_builds_dependency_graph(tmp_path):
    runtime = build_runtime(tmp_path)
    plan = WorkflowEngine(runtime).plan("تحقیق کن، کدنویسی کن، تست کن و در GitHub قرار بده")
    assert plan.selected_agent == "developer"
    assert [task.agent for task in plan.tasks] == ["research", "developer", "qa", "github"]
    assert plan.tasks[1].depends_on == [plan.tasks[0].id]
    assert plan.tasks[2].depends_on == [plan.tasks[1].id]
    assert plan.tasks[3].depends_on == [plan.tasks[2].id]
    assert len(plan.to_dict()["edges"]) == 3


def test_workflow_api_plan_and_run(tmp_path, monkeypatch):
    runtime = build_runtime(tmp_path)
    api = AgentTeamAPI(runtime.agent_team, runtime.registry_manager)
    app = create_app(api, runtime, project_store=ProjectStore(str(tmp_path / "platform.db")))
    app.config["TESTING"] = True

    plan_response = app.test_client().post(
        "/api/workflow/plan", json={"request": "تحقیق کن و کدنویسی کن و تست کن"}
    )
    assert plan_response.status_code == 200
    assert len(plan_response.get_json()["tasks"]) == 3

    class FakeReport:
        def to_dict(self):
            return {"status": "success", "tasks": []}

    monkeypatch.setattr(runtime, "run_tasks", lambda tasks: __import__("manager.report", fromlist=["ManagerReport"]).ManagerReport([]))
    run_response = app.test_client().post(
        "/api/workflow/run", json={"request": "یک پروژه بساز و تست کن"}
    )
    assert run_response.status_code == 200
    payload = run_response.get_json()
    assert payload["report"]["status"] == "pending"
    assert "workflow" in payload


def test_executor_retry_and_dependency_status(tmp_path, monkeypatch):
    runtime = build_runtime(tmp_path)
    calls = {"count": 0}

    def flaky(_tasks):
        calls["count"] += 1
        if calls["count"] == 1:
            raise RuntimeError("temporary failure")
        return ["done"]

    monkeypatch.setattr(runtime.loop, "run", flaky)
    first = Task(id="a", title="اول", agent="developer")
    second = Task(id="b", title="دوم", agent="developer", depends_on=["a"])
    runtime.executor.run([first, second])
    assert first.status == TaskStatus.SUCCESS
    assert first.attempts == 2
    assert second.status == TaskStatus.SUCCESS
