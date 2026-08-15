from __future__ import annotations

import json

from agents.github_agent import GitHubAgent
from agents.github_project_agent import GitHubProjectAgent
from manager.task import Task


class FakeAdapter:
    def __init__(self):
        self.calls = []

    def repository(self, repository):
        self.calls.append(("repository", repository))
        return {"full_name": repository}

    def file(self, repository, path, ref=None):
        self.calls.append(("file", repository, path, ref))
        return {"path": path}

    def put_file(self, repository, path, content, message, branch, sha=None):
        self.calls.append(("put_file", repository, path, content, message, branch, sha))
        return {"ok": True}

    def create_branch(self, repository, branch, base):
        self.calls.append(("create_branch", repository, branch, base))
        return {"branch": branch}

    def create_pull_request(self, repository, head, base, title, body="", draft=True):
        self.calls.append(("create_pr", repository, head, base, title, body, draft))
        return {"number": 1}

    def workflow_runs(self, repository, branch=None, workflow=None):
        self.calls.append(("workflow_runs", repository, branch, workflow))
        return {"workflow_runs": [{"conclusion": "success"}]}


def make_task(operation, **values):
    payload = {"operation": operation, "repository": "mydsoftware/AI-Agent-Manager", **values}
    return Task(id="t1", title="تست", description=json.dumps(payload, ensure_ascii=False), agent="github-project")


def test_project_agent_create_branch():
    adapter = FakeAdapter()
    agent = GitHubProjectAgent(GitHubAgent(adapter))
    result = agent.run(make_task("create_branch", branch="test/agent", base="feature/manager-core"))
    assert json.loads(result)["branch"] == "test/agent"
    assert adapter.calls[-1] == ("create_branch", "mydsoftware/AI-Agent-Manager", "test/agent", "feature/manager-core")


def test_project_agent_create_pr():
    adapter = FakeAdapter()
    agent = GitHubProjectAgent(GitHubAgent(adapter))
    result = agent.run(make_task("create_pr", head="test/agent", base="feature/manager-core", title="تست PR"))
    assert json.loads(result)["number"] == 1


def test_project_agent_workflow_status():
    adapter = FakeAdapter()
    agent = GitHubProjectAgent(GitHubAgent(adapter))
    result = agent.run(make_task("workflow_status", branch="feature/manager-core"))
    assert json.loads(result)["workflow_runs"][0]["conclusion"] == "success"
