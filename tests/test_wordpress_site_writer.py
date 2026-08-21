from agents.wordpress_site_writer import WordPressSiteWriter, WordPressWriterConfig


def test_wordpress_writer_uses_dedicated_ai_agent_endpoint(monkeypatch):
    captured = {}

    class FakeResponse:
        status = 200

        def read(self):
            return b'{"ok":true}'

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    def fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        captured["method"] = request.method
        captured["timeout"] = timeout
        captured["auth"] = request.headers.get("Authorization")
        return FakeResponse()

    monkeypatch.setattr("agents.wordpress_site_writer.urlopen", fake_urlopen)

    result = WordPressSiteWriter(
        WordPressWriterConfig("https://example.com", "admin", "app-pass")
    ).set_canonical("https://example.com/page", "https://example.com/page")

    assert result.success is True
    assert result.changed is True
    assert captured["url"].endswith("/wp-json/ai-agent-manager/v1/seo/canonical")
    assert captured["method"] == "POST"
    assert captured["auth"].startswith("Basic ")
