from manager.task import Task
from agents.developer_agent import DeveloperAgent
import json


def test_developer_agent_builds_autonomous_engineering_plan():
    task = Task(
        id="dev-1",
        title="تغییر کد",
        description=json.dumps({
            "repository": "mydsoftware/AI-Agent-Manager",
            "branch": "feature/test",
            "changes": [{
                "path": "tests/generated.txt",
                "content": "generated",
                "message": "test: generated change",
            }],
        }, ensure_ascii=False),
        agent="developer",
    )
    result = json.loads(DeveloperAgent().run(task))
    assert result["type"] == "development_plan"
    assert result["engineering_loop"] is True
    assert len(result["changes"]) == 1


def test_developer_agent_handles_incomplete_task():
    task = Task(id="dev-2", title="تحلیل", description="{}", agent="developer")
    result = json.loads(DeveloperAgent().run(task))
    assert result["engineering_loop"] is False
