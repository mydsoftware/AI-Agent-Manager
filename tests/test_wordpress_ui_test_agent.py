from pathlib import Path
import zipfile

from agents.wordpress_ui_test_agent import WordPressUITestAgent


def make_zip(path: Path, files: dict[str, str]) -> None:
    with zipfile.ZipFile(path, "w") as archive:
        for name, content in files.items():
            archive.writestr(name, content)


def test_ui_test_accepts_basic_ui(tmp_path: Path):
    package = tmp_path / "site.zip"
    make_zip(package, {
        "demo/front-page.php": '<html><meta name="viewport" content="width=device-width"><nav></nav><main><h1>Demo</h1></main></html>'
    })
    result = WordPressUITestAgent().run(str(package))
    assert result.passed is True
    assert "navigation-present" in result.checks
    assert "responsive-viewport" in result.checks


def test_ui_test_detects_missing_navigation(tmp_path: Path):
    package = tmp_path / "site.zip"
    make_zip(package, {"demo/front-page.php": '<main><h1>Demo</h1></main>'})
    result = WordPressUITestAgent().run(str(package))
    assert result.passed is False
    assert "missing:navigation" in result.findings
