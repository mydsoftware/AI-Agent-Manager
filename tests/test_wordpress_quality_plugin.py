from pathlib import Path

from agents.wordpress_quality_agent import WordPressQualityAgent


def test_quality_checks_plugin_header(tmp_path: Path):
    for name in ("functions.php", "front-page.php", "header.php", "footer.php"):
        (tmp_path / name).write_text("<?php\n", encoding="utf-8")
    (tmp_path / "style.css").write_text("/* Theme Name: Demo */", encoding="utf-8")
    plugin = tmp_path / "wp-content" / "plugins" / "demo" / "demo.php"
    plugin.parent.mkdir(parents=True)
    plugin.write_text("<?php\n/** Plugin Name: Demo */", encoding="utf-8")
    result = WordPressQualityAgent().validate(str(tmp_path))
    assert result.passed is True


def test_quality_detects_invalid_plugin_header(tmp_path: Path):
    for name in ("functions.php", "front-page.php", "header.php", "footer.php"):
        (tmp_path / name).write_text("<?php\n", encoding="utf-8")
    (tmp_path / "style.css").write_text("/* Theme Name: Demo */", encoding="utf-8")
    plugin = tmp_path / "wp-content" / "plugins" / "demo" / "demo.php"
    plugin.parent.mkdir(parents=True)
    plugin.write_text("<?php\n", encoding="utf-8")
    result = WordPressQualityAgent().validate(str(tmp_path))
    assert result.passed is False
    assert any(item.startswith("plugin-header:") for item in result.findings)
