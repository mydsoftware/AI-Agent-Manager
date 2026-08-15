from pathlib import Path
import http.server
import threading

from agents.wordpress_accessibility_test_agent import WordPressAccessibilityTestAgent


def test_accessibility_agent_accepts_basic_accessible_page(tmp_path: Path):
    (tmp_path / "index.html").write_text(
        '<html><head><title>Demo</title></head><body><h1>Demo</h1><img alt="Logo" src="logo.png">'
        '<label for="email">Email</label><input id="email"></body></html>',
        encoding="utf-8",
    )
    handler = lambda *args, **kwargs: http.server.SimpleHTTPRequestHandler(*args, directory=str(tmp_path), **kwargs)
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 18768), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        result = WordPressAccessibilityTestAgent().run("http://127.0.0.1:18768")
        assert result.passed is True
        assert "title-present" in result.checks
        assert "image-alt" in result.checks
        assert "form-labels" in result.checks
    finally:
        server.shutdown()
        server.server_close()
