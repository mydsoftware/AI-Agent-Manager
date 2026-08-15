from __future__ import annotations

import json

from agents.github_agent import GitHubAgent
from agents.github_project_agent import GitHubProjectAgent
from manager.task import Task


class FakeAdapter:
    def __init__(self):
        self.calls = []
        self.workflow_results = [
            {"workflow_runs": [{"status": "completed", "conclusion": "failure"}]},
            {"workflow_runs": [{"status": "completed", "conclusion": "success"}]},
        ]

    def repository(self, repository):
        return {"full_name": repository}

    def file(self, repository, path, ref=None):
        return {"path": path}

    def put_file(self, repository, path, content, message, branch, sha=None):
        self.calls.append(("put_file", path, branch, content))
        return {"ok": True}

    def create_branch(self, repository, branch, base):
        self.calls.append(("create_branch", branch, base))
        return {"branch": branch}

    def create_pull_request(self, repository, head, base, title, body="", draft=True):
        self.calls.append(("create_pr", head, base))
        return {"number": 10}

    def workflow_runs(self, repository, branch=None, workflow=None):
        self.calls.append(("workflow_runs", branch))
        return self.workflow_results.pop(0)


def test_engineering_loop_runs_repair_and_then_pr():
    adapter = FakeAdapter()
    agent = GitHubProjectAgent(GitHubAgent(adapter))
    task = Task(
        id="integration-1",
        title="تست چرخه مهندسی",
        agent="github-project",
        description=json.dumps({
            "operation": "engineering_loop",
            "repository": "mydsoftware/AI-Agent-Manager",
            "branch": "test/engineering-loop",
            "base": "feature/manager-core",
            "change": {"path": "tmp/change.txt", "content": "نسخه اول", "message": "تغییر آزمایشی", "branch": "test/engineering-loop"},
            "repair_change": {"path": "tmp/change.txt", "content": "نسخه اصلاح‌شده", "message": "اصلاح آزمایشی", "branch": "test/engineering-loop"},
            "pr": {"title": "PR آزمایشی"},
        }, ensure_ascii=False),
    )

    result = json.loads(agent.run(task))

    assert result["state"] == "done"
    assert result["attempts"] == 2
    assert result["ci_status"] == "success"
    assert any(call[0] == "create_branch" for call in adapter.calls)
    assert sum(call[0] == "put_file" for call in adapter.calls) == 2
    assert any(call[0] == "create_pr" for call in adapter.calls)
