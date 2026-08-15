from pathlib import Path
import http.server
import threading

from agents.wordpress_interaction_test_agent import WordPressInteractionTestAgent


def test_interaction_agent_checks_basic_controls(tmp_path: Path):
    (tmp_path / "index.html").write_text(
        '<html><body><a href="/next">Next</a><form><input name="q"></form><button>Send</button></body></html>',
        encoding="utf-8",
    )
    handler = lambda *args, **kwargs: http.server.SimpleHTTPRequestHandler(*args, directory=str(tmp_path), **kwargs)
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 18766), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        result = WordPressInteractionTestAgent().run("http://127.0.0.1:18766")
        assert result.passed is True
        assert "links-present" in result.checks
        assert "forms-present" in result.checks
        assert "buttons-present" in result.checks
    finally:
        server.shutdown()
        server.server_close()
