from __future__ import annotations

import json

from ai_gateway import AIResponse, AIGateway
from agents.qa_agent import QAAgent
from agents.registry import create_default_registry
from manager.task import Task


def fake_ai_complete(self, request, preferred=None):
    return AIResponse(
        content="تحلیل آزمایشی QA برای CI",
        provider=preferred or "test",
        model="test-model",
    )


def test_qa_agent_builds_engineering_plan(monkeypatch):
    monkeypatch.setattr(AIGateway, "complete", fake_ai_complete)
    task = Task(
        id="qa-1",
        title="اجرای تست",
        agent="qa",
        description=json.dumps({
            "repository": "mydsoftware/AI-Agent-Manager",
            "branch": "test/qa",
            "test_command": "pytest -q",
        }, ensure_ascii=False),
    )
    result = json.loads(QAAgent().run(task))
    assert result["type"] == "qa_plan"
    assert result["valid"] is True
    assert result["engineering_loop"] is True
    assert result["test_command"] == "pytest -q"
    assert result["ai_provider"] == "freellmapi"


def test_qa_agent_rejects_incomplete_task():
    task = Task(id="qa-2", title="تست ناقص", agent="qa", description="{}")
    result = json.loads(QAAgent().run(task))
    assert result["valid"] is False
    assert result["engineering_loop"] is False


def test_default_registry_contains_qa():
    registry = create_default_registry()
    assert "qa" in registry.names()
    assert registry.get("qa").name == "qa"
