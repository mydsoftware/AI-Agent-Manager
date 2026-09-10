from __future__ import annotations

from manager.project_factory import ProjectRepositoryFactory


class FakeGitHub:
    def __init__(self, existing: dict | None = None):
        self.existing = existing
        self.created = []
        self.puts = []
        self.dispatches = []

    def get_repository(self, repository: str):
        if self.existing and repository == self.existing["full_name"]:
            return self.existing
        raise RuntimeError("GitHub API خطای 404: Not Found")

    def create_repository(self, owner, name, description="", private=True, auto_init=True):
        repo = {
            "full_name": f"{owner}/{name}",
            "html_url": f"https://github.com/{owner}/{name}",
            "default_branch": "main",
        }
        self.created.append((owner, name, private, auto_init))
        self.existing = repo
        return repo

    def put_file(self, repository, path, content, message, branch, sha=None):
        self.puts.append((repository, path, branch))
        return {"ok": True}

    def repository_dispatch(self, repository, event_type, client_payload):
        self.dispatches.append((repository, event_type, client_payload))
        return {"ok": True}


def test_factory_creates_deterministic_repository_without_random_suffix():
    client = FakeGitHub()
    factory = ProjectRepositoryFactory(client=client, owner="mydsoftware")

    result = factory.create("My Test Site", "desc", "request")

    assert result.repository == "mydsoftware/my-test-site"
    assert result.reused_repository is False
    assert client.created == [("mydsoftware", "my-test-site", True, True)]


def test_factory_reuses_existing_repository_on_repeat():
    existing = {
        "full_name": "mydsoftware/my-test-site",
        "html_url": "https://github.com/mydsoftware/my-test-site",
        "default_branch": "main",
    }
    client = FakeGitHub(existing=existing)
    factory = ProjectRepositoryFactory(client=client, owner="mydsoftware")

    first = factory.create("My Test Site", "desc", "request")
    second = factory.create("My Test Site", "desc", "request")

    assert first.reused_repository is True
    assert second.reused_repository is True
    assert client.created == []
    assert all(item[0] == "mydsoftware/my-test-site" for item in client.puts)


def test_factory_propagates_non_404_errors_instead_of_creating_second_repository():
    class AuthFail(FakeGitHub):
        def get_repository(self, repository: str):
            raise RuntimeError("GitHub API خطای 401: Bad credentials")

    client = AuthFail()
    factory = ProjectRepositoryFactory(client=client, owner="mydsoftware")

    try:
        factory.create("My Test Site", "desc", "request")
    except RuntimeError as error:
        assert "401" in str(error)
    else:
        raise AssertionError("خطای احراز هویت نباید به Create Repository تبدیل شود")
    assert client.created == []
