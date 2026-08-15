from pathlib import Path

from agents.wordpress_runtime_browser_runner import WordPressRuntimeBrowserRunner


def test_runner_reports_runtime_setup(tmp_path: Path):
    (tmp_path / "index.html").write_text("<html><body><nav></nav><main>Demo</main></body></html>", encoding="utf-8")
    result = WordPressRuntimeBrowserRunner().run(str(tmp_path), 18765)
    assert result.runtime_url == "http://127.0.0.1:18765"
    assert result.started is True
    assert result.stopped is True
