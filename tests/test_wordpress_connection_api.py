from agents.wordpress_connection import WordPressConnectionCheck, WordPressConnectionConfig
from agents.wordpress_connection_api import WordPressConnectionApi


class FakeTester:
    def test(self, config):
        return WordPressConnectionCheck(True, True, True, "اتصال موفق")


def test_api_returns_connection_status():
    config = WordPressConnectionConfig("https://example.com", "admin", "app", "token")
    result = WordPressConnectionApi(FakeTester()).check(config)
    assert result == {
        "reachable": True,
        "authenticated": True,
        "writer_endpoint_available": True,
        "message": "اتصال موفق",
    }
