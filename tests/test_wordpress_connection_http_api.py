from agents.wordpress_connection import WordPressConnectionCheck
from agents.wordpress_connection_http_api import WordPressConnectionHttpApi


class FakeApi:
    def check(self, config):
        return {
            "reachable": True,
            "authenticated": True,
            "writer_endpoint_available": True,
            "message": "اتصال موفق",
        }


def test_http_api_rejects_missing_credentials():
    response = WordPressConnectionHttpApi(FakeApi()).post_check({"site_url": "https://example.com"})
    assert response.status == 400


def test_http_api_adapts_payload_to_connection_api():
    response = WordPressConnectionHttpApi(FakeApi()).post_check({
        "site_url": "https://example.com",
        "username": "admin",
        "application_password": "secret",
        "agent_token": "token",
    })
    assert response.status == 200
    assert response.body["authenticated"] is True
    assert "secret" not in str(response.body)
