from pathlib import Path

from agents.wordpress_local_runtime_agent import WordPressLocalRuntimeAgent


def test_local_runtime_prepares_static_runtime(tmp_path: Path):
    (tmp_path / "index.html").write_text("<main>Demo</main>", encoding="utf-8")
    result = WordPressLocalRuntimeAgent().prepare(str(tmp_path), 8765)
    assert result.prepared is True
    assert result.mode == "static-runtime"
    assert result.url == "http://127.0.0.1:8765"
    assert result.command is not None
