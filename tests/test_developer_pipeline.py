import json

from manager.application import ManagerApplication
from manager.task import Task


class FakeApplication(ManagerApplication):
    """نسخه آزمایشی برای بررسی زنجیره Developer تا GitHub Project."""

    def __init__(self):
        self.calls = []

    def run(self, task: Task) -> str:
        self.calls.append(task.agent)
        if task.agent == "developer":
            return json.dumps({
                "type": "development_plan",
                "repository": "mydsoftware/AI-Agent-Manager",
                "branch": "feature/test",
                "change": {"path": "demo.txt", "content": "تست", "message": "تست", "branch": "feature/test"},
                "engineering_loop": True,
            }, ensure_ascii=False)
        return json.dumps({"state": "done", "ci_status": "success"}, ensure_ascii=False)


def test_development_plan_contract_contains_engineering_fields():
    plan = {
        "type": "development_plan",
        "repository": "mydsoftware/AI-Agent-Manager",
        "branch": "feature/test",
        "change": {"path": "demo.txt", "content": "تست", "message": "تست", "branch": "feature/test"},
        "engineering_loop": True,
    }
    assert plan["engineering_loop"] is True
    assert plan["change"]["path"] == "demo.txt"
