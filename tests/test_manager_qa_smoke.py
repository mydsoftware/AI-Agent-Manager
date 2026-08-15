from __future__ import annotations

import json

from manager.application import ManagerApplication
from manager.task import Task


def test_manager_exposes_qa_agent():
    app = ManagerApplication()
    assert "qa" in app.agents()


def test_manager_routes_explicit_qa_task():
    app = ManagerApplication()
    task = Task(
        id="route-qa",
        title="اجرای تست QA",
        agent="qa",
        description=json.dumps({"repository": "example/repo", "branch": "test/qa"}),
    )
    assert app.route(task) == "qa"
