from __future__ import annotations

from services.activity_store import ActivityStore
from services.browser_qa import BrowserQA
from services.github_integration import GitHubConfig, GitHubIntegration
from services.vercel_deployment import VercelConfig, VercelDeploymentService


def test_approval_claim_is_atomic_and_releasable(tmp_path):
    store = ActivityStore(str(tmp_path / "manager.db"))
    approval = store.create_approval("project-1", "workflow.sensitive-run", "Deploy", fingerprint="fp")
    assert store.resolve_approval(approval["id"], "approved") is not None

    first = store.claim_approval(approval["id"], "fp")
    second = store.claim_approval(approval["id"], "fp")
    assert first is not None
    assert first["status"] == "claimed"
    assert second is None
    assert store.consume_approval(approval["id"]) ["status"] == "consumed"
    assert store.release_approval(approval["id"], "fp") is None


def test_failed_execution_can_release_claim(tmp_path):
    store = ActivityStore(str(tmp_path / "manager.db"))
    approval = store.create_approval("project-1", "workflow.sensitive-run", "Deploy", fingerprint="fp")
    store.resolve_approval(approval["id"], "approved")
    store.claim_approval(approval["id"], "fp")
    released = store.release_approval(approval["id"], "fp")
    assert released is not None
    assert released["status"] == "approved"


def test_ci_logs_are_sanitized_and_bounded():
    raw = "Authorization: Bearer SUPERSECRET token=abc password=hunter2 secret=xyz ghp_1234567890\n" + ("x" * 6000)
    sanitized = GitHubIntegration._sanitize_log(raw)
    assert len(sanitized) <= GitHubIntegration.MAX_AGENT_LOG_CHARS
    assert "SUPERSECRET" not in sanitized
    assert "hunter2" not in sanitized
    assert "ghp_1234567890" not in sanitized
    assert "[REDACTED]" in sanitized or "x" in sanitized


def test_github_branch_query_is_url_encoded():
    client = GitHubIntegration(GitHubConfig(token="token"))
    captured = {}

    def fake_request(method, path, payload=None):
        captured["path"] = path
        return {}

    client.request = fake_request
    client.workflow_runs("owner", "repo", "feature/a&b", 10)
    assert "branch=feature%2Fa%26b" in captured["path"]


def test_vercel_query_parameters_are_url_encoded():
    client = VercelDeploymentService(VercelConfig(token="token"))
    captured = []

    def fake_request(method, path, payload=None):
        captured.append(path)
        return {}

    client.request = fake_request
    client.project("my project", "team/a&b")
    client.deployments("my project", "team/a&b", 20)
    assert "teamId=team%2Fa%26b" in captured[0]
    assert "projectId=my+project" in captured[1]
    assert "teamId=team%2Fa%26b" in captured[1]


class _FakeRequest:
    def __init__(self, url):
        self.url = url
        self.aborted = False


class _FakeRoute:
    def __init__(self, url):
        self.request = _FakeRequest(url)
        self.aborted = False
        self.continued = False

    def abort(self):
        self.aborted = True

    def continue_(self):
        self.continued = True


class _FakePage:
    def __init__(self):
        self.handler = None

    def route(self, pattern, handler):
        assert pattern == "**/*"
        self.handler = handler


def test_browser_qa_uses_route_egress_guard(monkeypatch):
    page = _FakePage()
    qa = BrowserQA()
    qa._guard_requests(page)
    assert page.handler is not None

    monkeypatch.setattr("services.browser_qa.validate_public_http_url", lambda url: (_ for _ in ()).throw(ValueError("blocked")) if "127.0.0.1" in url else url)
    private_route = _FakeRoute("http://127.0.0.1:8080/internal")
    page.handler(private_route)
    assert private_route.aborted is True
    assert private_route.continued is False
