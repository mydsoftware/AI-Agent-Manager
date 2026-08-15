from pathlib import Path
import zipfile

from agents.wordpress_security_test_agent import WordPressSecurityTestAgent


def make_zip(path: Path, php: str) -> None:
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("demo/functions.php", php)


def test_security_agent_accepts_safe_php(tmp_path: Path):
    package = tmp_path / "safe.zip"
    make_zip(package, "<?php echo esc_html('ok');")
    result = WordPressSecurityTestAgent().run(str(package))
    assert result.passed is True
    assert "php-static-scan" in result.checks


def test_security_agent_detects_eval(tmp_path: Path):
    package = tmp_path / "unsafe.zip"
    make_zip(package, "<?php eval($_POST['code']);")
    result = WordPressSecurityTestAgent().run(str(package))
    assert result.passed is False
    assert any(item.startswith("dangerous:eval:") for item in result.findings)
