from pathlib import Path
import http.server
import threading

from agents.wordpress_responsive_test_agent import WordPressResponsiveTestAgent


def test_responsive_agent_checks_three_viewports(tmp_path: Path):
    (tmp_path / "index.html").write_text(
        '<html><head><meta name="viewport" content="width=device-width, initial-scale=1"></head>'
        '<body><main style="max-width:100%">Responsive</main></body></html>',
        encoding="utf-8",
    )
    handler = lambda *args, **kwargs: http.server.SimpleHTTPRequestHandler(*args, directory=str(tmp_path), **kwargs)
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 18767), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        result = WordPressResponsiveTestAgent().run("http://127.0.0.1:18767")
        assert result.passed is True
        assert set(result.checks) == {"viewport:mobile", "viewport:tablet", "viewport:desktop"}
    finally:
        server.shutdown()
        server.server_close()
