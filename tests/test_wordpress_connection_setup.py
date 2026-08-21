from agents.wordpress_connection import WordPressConnectionConfig
from agents.wordpress_connection_setup import WordPressConnectionSetup


def test_connection_setup_has_five_persian_steps():
    setup = WordPressConnectionSetup()
    assert setup.steps[0][0] == "آدرس سایت"
    assert setup.steps[-1][0] == "تست اتصال"
    assert setup.state(1).total_steps == 5
    assert setup.state(5).step == 5


def test_setup_delegates_connection_test(monkeypatch):
    class FakeTester:
        def test(self, config):
            return type("Check", (), {"reachable": True, "authenticated": True, "writer_endpoint_available": True})()

    monkeypatch.setattr("agents.wordpress_connection_setup.WordPressConnectionTester", lambda: FakeTester())
    result = WordPressConnectionSetup().test(
        WordPressConnectionConfig("https://example.com", "admin", "app", "token")
    )
    assert result.reachable is True
    assert result.authenticated is True
    assert result.writer_endpoint_available is True
