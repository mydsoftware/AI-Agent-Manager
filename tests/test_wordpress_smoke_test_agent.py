from pathlib import Path
import zipfile

from agents.wordpress_smoke_test_agent import WordPressSmokeTestAgent


def make_zip(path: Path, files: dict[str, str]) -> None:
    with zipfile.ZipFile(path, "w") as archive:
        for name, content in files.items():
            archive.writestr(name, content)


def test_smoke_test_accepts_valid_package(tmp_path: Path):
    package = tmp_path / "site.zip"
    make_zip(package, {
        "demo/style.css": "/* Theme Name: Demo */",
        "demo/functions.php": "<?php if (!defined('ABSPATH')) exit;",
        "demo/front-page.php": "<?php get_header(); ?><main>Demo</main><?php get_footer(); ?>",
    })
    result = WordPressSmokeTestAgent().run(str(package))
    assert result.passed is True
    assert "package-readable" in result.checks


def test_smoke_test_detects_incomplete_template(tmp_path: Path):
    package = tmp_path / "site.zip"
    make_zip(package, {
        "demo/style.css": "/* Theme Name: Demo */",
        "demo/functions.php": "<?php if (!defined('ABSPATH')) exit;",
        "demo/front-page.php": "<?php get_header(); ?>",
    })
    result = WordPressSmokeTestAgent().run(str(package))
    assert result.passed is False
    assert any(item.startswith("template-incomplete:") for item in result.findings)
