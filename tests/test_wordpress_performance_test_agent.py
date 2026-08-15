from pathlib import Path
import zipfile

from agents.wordpress_performance_test_agent import WordPressPerformanceTestAgent


def test_performance_agent_accepts_small_package(tmp_path: Path):
    package = tmp_path / "site.zip"
    with zipfile.ZipFile(package, "w") as archive:
        archive.writestr("demo/style.css", "body{}")
        archive.writestr("demo/app.js", "console.log('ok')")
    result = WordPressPerformanceTestAgent().run(str(package))
    assert result.passed is True
    assert result.metrics["assets"] == 2


def test_performance_agent_detects_too_many_assets(tmp_path: Path):
    package = tmp_path / "site.zip"
    with zipfile.ZipFile(package, "w") as archive:
        for i in range(3):
            archive.writestr(f"demo/{i}.js", "x")
    result = WordPressPerformanceTestAgent(max_assets=2).run(str(package))
    assert result.passed is False
    assert "too-many-assets:3" in result.findings
