from __future__ import annotations

from api.http import create_app


class FakeTeamAPI:
    def list_agents(self):
        return [{"name": "developer", "enabled": True}]

    def enable(self, name):
        return {"name": name, "enabled": True}

    def disable(self, name):
        return {"name": name, "enabled": False}


class FakeRuntime:
    def run(self, request, agent=None):
        raise AssertionError("dashboard route test must not execute an LLM")


def test_dashboard_is_served():
    app = create_app(FakeTeamAPI(), runtime=FakeRuntime())
    app.config["TESTING"] = True
    client = app.test_client()

    response = client.get("/")
    assert response.status_code == 200
    assert "AI-Agent-Manager" in response.get_data(as_text=True)
    assert 'dir="rtl"' in response.get_data(as_text=True)

    response = client.get("/dashboard/static/app.css")
    assert response.status_code == 200
    assert "sidebar" in response.get_data(as_text=True)


def test_dashboard_api_contract_is_available():
    app = create_app(FakeTeamAPI(), runtime=FakeRuntime())
    app.config["TESTING"] = True
    client = app.test_client()

    assert client.get("/api/health").get_json() == {"status": "ok"}
    assert client.get("/api/agents").get_json() == [{"name": "developer", "enabled": True}]
