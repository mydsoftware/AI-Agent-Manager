import json

from ai_gateway import AIResponse, AIGateway
from agents.developer_agent import DeveloperAgent
from manager.task import Task


def fake_ai_complete(request, preferred=None):
    return AIResponse(
        content="تحلیل آزمایشی توسعه برای CI",
        provider=preferred or "test",
        model="test-model",
    )


def test_developer_agent_builds_engineering_plan(monkeypatch):
    monkeypatch.setattr(AIGateway, "complete", fake_ai_complete)
    task = Task(
        id="dev-1",
        title="تغییر کد",
        description=json.dumps({
            "repository": "mydsoftware/AI-Agent-Manager",
            "branch": "feature/test",
            "change": "افزودن یک قابلیت آزمایشی",
        }, ensure_ascii=False),
        agent="developer",
    )
    result = json.loads(DeveloperAgent().run(task))
    assert result["type"] == "development_plan"
    assert result["engineering_loop"] is True
    assert result["ai_provider"] == "omniroute"
    assert result["ai_model"] == "test-model"


def test_developer_agent_handles_incomplete_task():
    task = Task(id="dev-2", title="تحلیل", description="{}", agent="developer")
    result = json.loads(DeveloperAgent().run(task))
    assert result["engineering_loop"] is False
