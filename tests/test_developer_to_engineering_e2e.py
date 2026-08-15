from __future__ import annotations

import json

from agents.developer_agent import DeveloperAgent
from agents.github_project_agent import GitHubProjectAgent
from manager.engineering_loop import EngineeringLoop
from manager.task import Task


class FakeGitHubAgent:
    """شبیه‌ساز GitHub برای آزمون انتها‌به‌انتها بدون تغییر Repository واقعی."""

    def __init__(self):
        self.calls = []
        self.ci = iter(["failure", "success"])

    def run(self, task: Task) -> str:
        command = json.loads(task.description)
        self.calls.append(command)
        action = command["action"]
        if action == "workflow_runs":
            status = next(self.ci)
            return json.dumps({"workflow_runs": [{"conclusion": status}]})
        return json.dumps({"ok": True, "action": action})


def test_developer_plan_reaches_engineering_loop_and_pr():
    task = Task(
        id="e2e-1",
        title="اجرای تغییر آزمایشی",
        agent="developer",
        description=json.dumps({
            "repository": "mydsoftware/AI-Agent-Manager",
            "branch": "test/e2e",
            "change": "تغییر آزمایشی",
        }, ensure_ascii=False),
    )

    plan = json.loads(DeveloperAgent().run(task))
    assert plan["engineering_loop"] is True

    fake = FakeGitHubAgent()
    project = GitHubProjectAgent(github=fake, engineering_loop=EngineeringLoop(max_attempts=2))
    engineering_task = Task(
        id="e2e-2",
        title="اجرای چرخه",
        agent="github-project",
        description=json.dumps({
            "operation": "engineering_loop",
            "repository": plan["repository"],
            "branch": plan["branch"],
            "base": "main",
            "change": {
                "path": "tests/e2e_marker.txt",
                "content": "نشانگر آزمایش انتها‌به‌انتها",
                "message": "test: اجرای آزمایش انتها‌به‌انتها",
                "branch": plan["branch"],
            },
            "repair_change": {
                "path": "tests/e2e_marker.txt",
                "content": "اصلاح آزمایش انتها‌به‌انتها",
                "message": "fix: اصلاح آزمایش انتها‌به‌انتها",
                "branch": plan["branch"],
            },
            "pr": {"title": "PR آزمایش انتها‌به‌انتها", "draft": True},
        }, ensure_ascii=False),
    )

    result = json.loads(project.run(engineering_task))
    assert result["state"] == "done"
    assert result["attempts"] == 2
    assert result["ci_status"] == "success"
    assert [call["action"] for call in fake.calls] == [
        "create_branch", "put_file", "workflow_runs", "put_file", "workflow_runs", "create_pr"
    ]
