from agents.wordpress_connection_check import WordPressConnectionChecker


def test_checker_uses_read_only_options_request(monkeypatch):
    captured = {}

    class Response:
        status = 204
        def __enter__(self): return self
        def __exit__(self, *args): return False

    def fake_urlopen(request, timeout):
        captured["method"] = request.method
        captured["url"] = request.full_url
        captured["timeout"] = timeout
        return Response()

    monkeypatch.setattr("agents.wordpress_connection_check.urlopen", fake_urlopen)
    result = WordPressConnectionChecker().check("https://example.com", "token")

    assert result.reachable is True
    assert result.endpoint_available is True
    assert captured["method"] == "OPTIONS"
    assert captured["url"].endswith("/wp-json/ai-agent-manager/v1/seo/canonical")
