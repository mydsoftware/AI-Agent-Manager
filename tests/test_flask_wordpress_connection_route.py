from agents.wordpress_connection_http_api import WordPressConnectionHttpApi
from api.http import create_app


class FakeTeamApi:
    def list_agents(self):
        return []

    def enable(self, name):
        return {"enabled": name}

    def disable(self, name):
        return {"disabled": name}


class FakeConnectionApi:
    def post_check(self, payload):
        return type("Response", (), {
            "status": 200,
            "body": {
                "reachable": True,
                "authenticated": True,
                "writer_endpoint_available": True,
                "message": "اتصال موفق",
            },
        })()


def test_flask_exposes_wordpress_connection_check_route():
    app = create_app(FakeTeamApi(), wordpress_connection_api=FakeConnectionApi())
    client = app.test_client()
    response = client.post(
        "/api/wordpress/connection/check",
        json={
            "site_url": "https://example.com",
            "username": "admin",
            "application_password": "secret",
            "agent_token": "token",
        },
    )
    assert response.status_code == 200
    assert response.get_json()["authenticated"] is True


def test_flask_rejects_non_object_payload():
    app = create_app(FakeTeamApi(), wordpress_connection_api=FakeConnectionApi())
    response = app.test_client().post(
        "/api/wordpress/connection/check",
        json=["bad"],
    )
    assert response.status_code == 400
