import json

from manager.application import ManagerApplication
from manager.task import Task


def test_github_engineering_task_is_activated():
    app = ManagerApplication()
    task = Task(
        id="eng-1",
        title="اصلاح پروژه GitHub",
        description=json.dumps({
            "repository": "mydsoftware/AI-Agent-Manager",
            "branch": "test/manager-loop",
            "change": {"path": "README.md", "content": "تست", "message": "test", "sha": "sha"},
        }, ensure_ascii=False),
        agent=None,
    )

    decision = app.intelligent_router.select(task)
    prepared = app._prepare_task(task, decision.agent, decision.engineering)
    command = json.loads(prepared.description)

    assert decision.agent == "github-project"
    assert decision.engineering is True
    assert command["operation"] == "engineering_loop"


def test_non_engineering_github_task_is_not_forced_into_loop():
    app = ManagerApplication()
    task = Task(
        id="read-1",
        title="خواندن فایل GitHub",
        description=json.dumps({
            "operation": "read_file",
            "repository": "mydsoftware/AI-Agent-Manager",
            "path": "README.md",
        }, ensure_ascii=False),
        agent=None,
    )

    decision = app.intelligent_router.select(task)
    prepared = app._prepare_task(task, decision.agent, decision.engineering)
    command = json.loads(prepared.description)

    assert command["operation"] == "read_file"
