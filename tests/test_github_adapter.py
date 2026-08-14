from __future__ import annotations

from adapters.github_adapter import GitHubAdapter


class FakeGitHubClient:
    def __init__(self):
        self.calls = []

    def get_repository(self, repository):
        self.calls.append(("repository", repository))
        return {"full_name": repository}

    def get_file(self, repository, path, ref=None):
        self.calls.append(("file", repository, path, ref))
        return {"path": path, "ref": ref}

    def put_file(self, repository, path, content, message, branch, sha=None):
        self.calls.append(("put_file", repository, path, content, message, branch, sha))
        return {"commit": {"sha": "commit-sha"}}

    def create_branch(self, repository, branch, base):
        self.calls.append(("create_branch", repository, branch, base))
        return {"ref": f"refs/heads/{branch}"}

    def create_pull_request(self, repository, head, base, title, body="", draft=True):
        self.calls.append(("create_pr", repository, head, base, title, body, draft))
        return {"number": 123, "draft": draft}


def test_create_branch_is_forwarded():
    client = FakeGitHubClient()
    adapter = GitHubAdapter(client)
    result = adapter.create_branch("mydsoftware/AI-Agent-Manager", "test/branch", "feature/manager-core")
    assert result["ref"] == "refs/heads/test/branch"
    assert client.calls[-1] == ("create_branch", "mydsoftware/AI-Agent-Manager", "test/branch", "feature/manager-core")


def test_create_pull_request_is_forwarded():
    client = FakeGitHubClient()
    adapter = GitHubAdapter(client)
    result = adapter.create_pull_request(
        "mydsoftware/AI-Agent-Manager",
        "test/branch",
        "feature/manager-core",
        "PR آزمایشی",
        "توضیح آزمایشی",
        True,
    )
    assert result["number"] == 123
    assert result["draft"] is True
