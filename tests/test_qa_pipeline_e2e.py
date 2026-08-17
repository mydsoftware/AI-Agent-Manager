from __future__ import annotations

import json

from ai_gateway import AIResponse, AIGateway
from agents.qa_agent import QAAgent
from manager.application import ManagerApplication
from manager.task import Task


class FakeExecutor:
    def __init__(self):
        self.tasks = []

    def run(self, tasks):
        self.tasks.extend(tasks)
        task = tasks[0]
        if task.agent == "qa":
            return [json.dumps({
                "type": "qa_plan",
                "valid": True,
                "engineering_loop": True,
                "repository": "example/repo",
                "branch": "test/qa-pipeline",
                "base": "main",
                "workflow": "ci.yml",
                "change": {"path": "tests/qa_marker.txt", "content": "qa", "message": "test: qa", "branch": "test/qa-pipeline"},
                "repair_change": {"path": "tests/qa_marker.txt", "content": "repair", "message": "fix: qa", "branch": "test/qa-pipeline"},
                "pr": {"title": "QA pipeline", "draft": True},
            })]
        return [json.dumps({"state": "done", "attempts": 1, "ci_status": "success", "error": None})]


def fake_ai_complete(self, request, preferred=None):
    return AIResponse(
        content="تحلیل آزمایشی QA برای آزمون انتها‌به‌انتها",
        provider=preferred or "test",
        model="test-model",
    )


def test_manager_routes_qa_into_engineering_loop():
    app = ManagerApplication()
    fake = FakeExecutor()
    app.executor = fake

    task = Task(
        id="qa-e2e",
        title="آزمون QA",
        agent="qa",
        description=json.dumps({
            "repository": "example/repo",
            "branch": "test/qa-pipeline",
            "test_command": "pytest -q",
        }, ensure_ascii=False),
    )

    result = json.loads(app.run(task))
    assert result["state"] == "done"
    assert result["ci_status"] == "success"
    assert [item.agent for item in fake.tasks] == ["qa", "github-project"]


def test_qa_agent_still_produces_valid_plan(monkeypatch):
    monkeypatch.setattr(AIGateway, "complete", fake_ai_complete)
    task = Task(
        id="qa-plan",
        title="برنامه QA",
        agent="qa",
        description=json.dumps({
            "repository": "example/repo",
            "branch": "test/qa",
            "test_command": "pytest -q",
        }, ensure_ascii=False),
    )
    result = json.loads(QAAgent().run(task))
    assert result["valid"] is True
    assert result["engineering_loop"] is True
